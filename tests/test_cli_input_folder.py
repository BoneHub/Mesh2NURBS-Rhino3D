import os
import subprocess
import tempfile


def run_cli(input_path):
    """Helper function to run the CLI script"""
    return subprocess.run(
        ["python", "rhinoMeshTools/cli_full.py", "--input", input_path, "--keepopen"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_empty_folder_does_not_crash():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_cli(tmpdir)
        assert result.returncode == 0  # Should not crash
        assert "Progress:" not in result.stdout  # Nothing should be processed


def test_invalid_file_in_folder_skips_gracefully():
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_path = os.path.join(tmpdir, "not_a_mesh.txt")
        with open(invalid_path, "w") as f:
            f.write("Not a real mesh file")
        valid_path = os.path.join(tmpdir, "mesh.obj")
        with open(valid_path, "w") as b:
            b.write("""
                    v 0 0 0
                    v 1 0 0
                    v 1 1 0
                    v 0 1 0
                    v 0 0 1
                    v 1 0 1
                    v 1 1 1
                    v 0 1 1
                    f 1 2 3 4
                    f 5 6 7 8
                    f 1 5 8 4
                    f 2 6 7 3
                    f 1 2 6 5
                    f 4 3 7 8
                    """)
        result = run_cli(tmpdir)
        assert result.returncode == 0
        output_dir = os.path.join(tmpdir, "results\\CADModels")
        foundValidInput = False
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if "mesh" in file:
                    foundValidInput = True
                    break
        assert foundValidInput, "Valid mesh file did not produce output"
