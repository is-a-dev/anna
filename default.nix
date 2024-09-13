{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    python312Packages.virtualenv
  ];

  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
      python -m venv venv
      source venv/bin/activate
      # Upgrade pip to the latest version
      pip install --upgrade pip
      # Install Python dependencies via pip
      pip install nextcord psl-dns python-dotenv onami aiohttp psycopg2-binary nextcord-ext-help-commands nextcord-ext-menus python-whois forex-python setuptools aiohttp aiosignal aiosqlite attrs cfgv distlib filelock frozenlist identify idna multidict nodeenv platformdirs pre-commit pyyaml typing-extensions virtualenv pymongo motor flask
    else
      # Activate the virtual environment if it already exists
      source venv/bin/activate
    python3 anna
    fi
  '';
}
