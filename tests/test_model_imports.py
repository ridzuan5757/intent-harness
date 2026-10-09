"""Importing the tools and their plugins must not load a model package or the core."""

import subprocess
import sys


def loaded_after(statement):
    code = (
        "import sys\n"
        f"{statement}\n"
        "names = []\n"
        "for name in sys.modules:\n"
        "    top = name.split('.')[0]\n"
        "    if top in ('torch', 'transformers', 'intent_harness'):\n"
        "        names.append(top)\n"
        "print(','.join(sorted(set(names))))\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def test_tools_package_loads_no_model_package():
    assert loaded_after("import intent_harness_tools") == ""


def test_model_tool_modules_load_no_model_package_at_import():
    assert loaded_after(
        "import intent_harness_tools.sam3, intent_harness_tools.grounding_dino, "
        "intent_harness_tools.sam3_plugin, intent_harness_tools.grounding_dino_plugin"
    ) == ""
