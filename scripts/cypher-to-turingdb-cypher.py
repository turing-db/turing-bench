import os
import argparse
import json


def infer_type(value):
    """Infer the supported type of a value."""
    if isinstance(value, bool):
        return "Bool"
    elif isinstance(value, int):
        return "Int64"
    elif isinstance(value, float):
        return "Double"
    else:
        # Everything else (dates, lists, etc.) becomes String
        return "String"


def format_value(value, target_type):
    """Format a value for Cypher output."""
    if target_type == "String":
        str_val = str(value)
        # Escape backslashes and quotes
        str_val = str_val.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{str_val}"'
    elif target_type == "Bool":
        return "true" if value else "false"
    elif target_type in ["Int64", "Double"]:
        return str(value)
    return f'"{str(value)}"'


def escape_property_name(name):
    """Escape property names that need backticks."""
    # Properties with spaces, parens, or special chars need backticks
    if ' ' in name or '(' in name or ')' in name or '-' in name:
        return f"`{name}`"
    return name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, metavar="input-file")
    parser.add_argument("--output-file", type=str, default="/tmp/output.tdbcypher")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # First pass: collect all data and detect type conflicts
    nodes = []
    relationships = []
    property_types = {}  # property_name -> set of (type, context)
    
    with open(input_file, "r") as inp:
        for line in inp:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            
            if data["type"] == "node":
                nodes.append(data)
                # Track property types
                for prop_name, prop_value in data.get("properties", {}).items():
                    prop_type = infer_type(prop_value)
                    if prop_name not in property_types:
                        property_types[prop_name] = set()
                    property_types[prop_name].add(prop_type)
            
            elif data["type"] == "relationship":
                relationships.append(data)
                # Track property types
                for prop_name, prop_value in data.get("properties", {}).items():
                    prop_type = infer_type(prop_value)
                    if prop_name not in property_types:
                        property_types[prop_name] = set()
                    property_types[prop_name].add(prop_type)
    
    # Determine which properties have conflicts
    conflicting_properties = {name for name, types in property_types.items() if len(types) > 1}
    
    # Build the CREATE statement
    with open(output_file, "w") as out:
        out.write("CHANGE NEW\n")
        out.write("checkout change-0\n")
        out.write("CREATE")
        
        # Write nodes
        for i, node in enumerate(nodes):
            node_id = node["id"]
            labels = ":".join(node.get("labels", []))
            
            # Build properties
            props = node.get("properties", {})
            prop_strs = []
            for prop_name, prop_value in props.items():
                prop_type = infer_type(prop_value)
                
                # Check if this property has type conflicts
                if prop_name in conflicting_properties:
                    # Append type to property name
                    formatted_name = escape_property_name(f"{prop_name} ({prop_type})")
                else:
                    formatted_name = escape_property_name(prop_name)
                
                formatted_value = format_value(prop_value, prop_type)
                prop_strs.append(f"{formatted_name}: {formatted_value}")
            
            props_str = " {" + ", ".join(prop_strs) + "}" if prop_strs else ""
            
            if labels:
                node_str = f"(n{node_id}:{labels}{props_str})"
            else:
                node_str = f"(n{node_id}{props_str})"
            
            out.write(node_str)
            if i < len(nodes) - 1 or relationships:
                out.write(",")
        
        # Write relationships
        for i, rel in enumerate(relationships):
            rel_id = rel["id"]
            label = rel["label"]
            start_id = rel["start"]["id"]
            end_id = rel["end"]["id"]
            
            # Build properties
            props = rel.get("properties", {})
            prop_strs = []
            for prop_name, prop_value in props.items():
                prop_type = infer_type(prop_value)
                
                # Check if this property has type conflicts
                if prop_name in conflicting_properties:
                    # Append type to property name
                    formatted_name = escape_property_name(f"{prop_name} ({prop_type})")
                else:
                    formatted_name = escape_property_name(prop_name)
                
                formatted_value = format_value(prop_value, prop_type)
                prop_strs.append(f"{formatted_name}: {formatted_value}")
            
            props_str = " {" + ", ".join(prop_strs) + "}" if prop_strs else ""
            
            rel_str = f"(n{start_id})-[r{rel_id}:{label}{props_str}]->(n{end_id})"
            
            out.write(rel_str)
            if i < len(relationships) - 1:
                out.write(",")
        out.write("\n")
        out.write("CHANGE SUBMIT\n");
    
    print(f"Generated Cypher CREATE statement written to {output_file}")
    print(f"Nodes: {len(nodes)}, Relationships: {len(relationships)}")
    if conflicting_properties:
        print(f"Properties with type conflicts: {', '.join(sorted(conflicting_properties))}")
