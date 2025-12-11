from pathlib import Path

def load_template(template_name: str, variables: dict) -> str:
    base_path = Path(__file__).resolve().parent.parent / "templates"
    file_path = base_path / template_name

    if not file_path.exists():
        raise FileNotFoundError(f"❌ Template não encontrado: {file_path}")

    template = file_path.read_text(encoding="utf-8")

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder not in template:
            print(f"⚠️ Aviso: placeholder {placeholder} não encontrado no template.")
        template = template.replace(placeholder, str(value))



    return template
