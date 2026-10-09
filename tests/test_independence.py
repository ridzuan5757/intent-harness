"""The tools package must not import any other package of this repository."""

import subprocess
import sys


def test_tools_package_loads_no_core_module():
    code = (
        "import sys\n"
        "import intent_harness_tools\n"
        "loaded = []\n"
        "for name in sys.modules:\n"
        "    if name == 'intent_harness' or name.startswith('intent_harness.'):\n"
        "        loaded.append(name)\n"
        "print(','.join(loaded))\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == ""
