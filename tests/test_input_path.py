import unittest
import os
import platform

# This function simulates the initial processing of the input path argument
# as done in cli_fix.py and cli_full.py before further use.
def process_cli_input_path(path_string):
    """
    Processes a path string similar to how CLI scripts might handle an --input argument.
    Returns the absolute path if the input is a valid string and abspath succeeds,
    otherwise returns None.
    """
    if not isinstance(path_string, str) or not path_string: # Handles empty string or wrong type
        return None

    try:
        # Key operation performed by the CLI scripts on the input path
        abs_path = os.path.abspath(path_string)
        
        # Note: os.path.abspath is quite tolerant. It will process strings with
        # characters that are invalid for filenames (e.g., '<', '>', '?')
        # without raising an error. Such paths would fail at the file system level.
        # This function primarily tests if abspath can process the string.
        return abs_path
    except TypeError: # os.path.abspath can raise TypeError for some non-string inputs if not caught above
        return None
    except Exception:
        # Catch any other unexpected errors during path processing
        return None

class TestInputPath(unittest.TestCase):
    def test_valid_paths_without_spaces(self):
        """Test paths without spaces that should be accepted."""
        paths = [
            "C:\\temp\\file.ply",
            "relative_path\\file.obj",
            "..\\parent_folder\\data.ply",
            "file_in_current_dir.txt",
        ]
        if platform.system() != "Windows": # Add Unix-style paths if not on Windows
            paths.extend([
                "/usr/local/data/model.stl",
                "somedir/anotherfile.mesh",
                "../anotherparent/resource.dat"
            ])

        for p in paths:
            with self.subTest(path=p):
                processed_path = process_cli_input_path(p)
                self.assertIsNotNone(processed_path, f"Path '{p}' should be accepted and processed.")
                self.assertTrue(os.path.isabs(processed_path), f"Processed path '{processed_path}' for '{p}' should be absolute.")

    def test_valid_paths_with_spaces(self):
        """Test paths with spaces that should be accepted."""
        paths = [
            "C:\\my folder\\my project file.ply",
            "D:\\research data\\subject 01 data.stl",
            # Changed C: to C:\\ to make the path absolute from the drive root
            os.path.join("C:\\", "Program Files", "My Application", "input with spaces.obj"),
            "relative path with spaces\\another file.mesh",
            "..\\parent folder with spaces\\data file.ply",
        ]
        if platform.system() != "Windows":
            paths.extend([
                "/home/user/my documents/project report.docx",
                "some dir with spaces/another file with spaces.txt",
                "../parent dir with spaces/resource file.dat"
            ])
            
        for p in paths:
            with self.subTest(path=p):
                processed_path = process_cli_input_path(p)
                self.assertIsNotNone(processed_path, f"Path '{p}' with spaces should be accepted and processed.")
                self.assertTrue(os.path.isabs(processed_path), f"Processed path '{processed_path}' for '{p}' should be absolute.")
                if " " in p:
                    # Check that spaces are preserved in the output path.
                    # This is a basic check; abspath normalizes paths, but spaces in names should remain.
                    original_name_part_with_space = next((part for part in p.replace("\\", "/").split("/") if " " in part), None)
                    if original_name_part_with_space:
                         self.assertTrue(original_name_part_with_space in processed_path.replace("\\", "/"),
                                         f"Path component with spaces from '{p}' seems altered in '{processed_path}'")

    def test_empty_or_invalid_type_paths(self):
        """Test paths that are empty or of invalid type."""
        invalid_inputs = [
            "",      # Empty path
            None,    # None value
            123,     # Integer type
            [],      # List type
            object() # Object type
        ]
        for p in invalid_inputs:
            with self.subTest(path_input=str(p)): # Use str(p) for subtest name clarity
                self.assertIsNone(process_cli_input_path(p), f"Input '{str(p)}' should be rejected (return None).")

    def test_paths_with_problematic_characters(self):
        """
        Test paths with characters that are often problematic for file systems.
        os.path.abspath itself might process these strings, but they would likely fail
        during actual file operations.
        """
        # These characters are typically invalid in Windows filenames/paths.
        # On Unix-like systems, some of these might be permissible in filenames.
        problematic_chars_paths = [
            "C:\\temp\\file_with_invalid_char<>.ply",
            "D:\\another_invalid?path.stl",
            "E:\\path_with_star*.obj",
            "F:\\path_with_pipe|.data",
            "G:\\path_with_quote\".txt",
            # "H:\\path_with_colon_in_name:file.txt", # Colon is special for drives on Windows
        ]
        if platform.system() == "Windows":
            for p in problematic_chars_paths:
                with self.subTest(path=p):
                    processed_path = process_cli_input_path(p)
                    # os.path.abspath will likely return a path string including these characters
                    self.assertIsNotNone(processed_path, f"Path '{p}' is processed by abspath, though problematic for FS.")
                    # Check that the problematic character is still in the processed path
                    problem_char = next((char for char in ['<', '>', '?', '*', '|', '"'] if char in p), None)
                    if problem_char:
                        self.assertTrue(problem_char in processed_path, 
                                        f"Problematic char '{problem_char}' from '{p}' should be in processed path '{processed_path}'.")
        # Add specific tests for other OS if needed, as character validity rules differ.

if __name__ == '__main__':
    unittest.main()