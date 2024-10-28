{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    python312Packages.virtualenv
  ];

  shellHook = ''
    if [ ! -d "venv" ]; then
      python -m venv venv
      source venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt
    else
      source venv/bin/activate
    cd anna/extensions
    if [ ! -d "takina" ]; then
      git clone https://github.com/orangci/takina
    fi
    cd ../..
    python3 anna
    fi
  '';
}
