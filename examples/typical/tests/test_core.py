import sys
from pathlib import Path

# Insert src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from typical_example.core import get_environment


def test_environment_initialization():
    env = get_environment()
    assert env is not None
    # the analyzer isn't registered, but the SignatureExtension is
    assert "jinja2_type_gen.extension.SignatureExtension" in [
        type(ext).__module__ + "." + type(ext).__name__
        for ext in env.extensions.values()
    ]
