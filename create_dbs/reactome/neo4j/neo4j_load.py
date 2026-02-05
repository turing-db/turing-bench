#!/usr/bin/env python3
"""Setup Reactome database for Neo4j v5"""

import subprocess
import os
from pathlib import Path
import tempfile
import zstandard as zstd

class ReactomeNeo4jSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.repo_root = self.script_dir.parent.parent.parent
        self.neo4j_home = self.repo_root / "install" / "neo4j-build"
        self.dump_file = self.script_dir / "reactome.graphdb.dump"
        self.local_data_dir = self.script_dir / "data"
        self.neo4j_data_dir = self.neo4j_home / "data" / "databases" / "reactome"
        self.neo4j_conf = self.neo4j_home / "conf" / "neo4j.conf"
        self.dump_url = "https://reactome.org/download/current/reactome.graphdb.dump"
    
    def download_dump(self):
        if self.dump_file.exists():
            print(f"Reactome dump already exists at {self.dump_file}")
            return
        print("Downloading Reactome dump...")
        subprocess.run(["wget", "-O", str(self.dump_file), self.dump_url], check=True)
    
    def extract_dump(self):
        print("Extracting Reactome dump...")
        
        # Check if zstd is available
        result = subprocess.run(["which", "unzstd"], capture_output=True)
        if result.returncode != 0:
            print("Error: unzstd not found. Install with: sudo apt-get install zstandard")
            raise RuntimeError("zstandard not installed")
        
        temp_dir = tempfile.mkdtemp()
        extracted_file = Path(temp_dir) / "reactome.dump"
        
        subprocess.run(["unzstd", "-d", str(self.dump_file), "-o", str(extracted_file)], check=True)
        
        return temp_dir
    
    def configure_neo4j(self):
        print("Configuring neo4j.conf...")
        config_lines = [
            "initial.dbms.default_database=reactome",
            "db.recovery.fail_on_missing_files=false",
            "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false"
        ]
        
        with open(self.neo4j_conf, 'r') as f:
            content = f.read()
        
        if config_lines[0] not in content:
            with open(self.neo4j_conf, 'a') as f:
                f.write("\n# Reactome configuration\n")
                for line in config_lines:
                    f.write(f"{line}\n")
    
    def load_dump(self):
        print("Loading Reactome dump into Neo4j...")
        env = os.environ.copy()
        env_sh = self.repo_root / "env.sh"
        
        # Point to the original compressed dump file, not the extracted one
        dump_dir = self.dump_file.parent
        cmd = f"source {env_sh} && cd {self.neo4j_home} && ./bin/neo4j-admin database load --from-path={dump_dir} reactome --overwrite-destination"
        subprocess.run(cmd, shell=True, env=env, check=True, executable='/bin/bash')
        
    def migrate_database(self):
        print("Running Neo4j migration...")
        env = os.environ.copy()
        env_sh = self.repo_root / "env.sh"
        
        cmd = f"source {env_sh} && cd {self.neo4j_home} && ./bin/neo4j-admin database migrate --force-btree-indexes-to-range reactome"
        subprocess.run(cmd, shell=True, env=env, check=True, executable='/bin/bash')
    
    def create_symlink(self):
        print("Creating symbolic link...")
        self.local_data_dir.parent.mkdir(parents=True, exist_ok=True)
        if self.local_data_dir.exists() or self.local_data_dir.is_symlink():
            self.local_data_dir.unlink()
        self.local_data_dir.symlink_to(self.neo4j_data_dir)
    
    def run(self):
        print("=== Reactome Neo4j v5 Setup ===")
        # ... dependency check ...
        self.download_dump()
        # Remove: dump_dir = self.extract_dump()
        self.configure_neo4j()
        self.load_dump()  # No argument needed anymore
        self.migrate_database()
        self.create_symlink()
        print(f"=== Setup Complete ===")
        print(f"Data available at: {self.local_data_dir}")

if __name__ == "__main__":
    setup = ReactomeNeo4jSetup()
    setup.run()