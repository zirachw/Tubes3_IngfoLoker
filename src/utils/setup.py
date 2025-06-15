import os
import shutil
import zipfile

class SetupPDFData:
    def __init__(self, archive_path='data/archive.zip', extract_to='data'):
        self.archive_path = archive_path
        self.extract_to = extract_to
        self.moved_count = 0
        self.duplicate_count = 0
        self.subdirs = []
        # After extraction: data/data/data/typeN
        self.base_data_dir = os.path.join(self.extract_to, 'data', 'data')
        # Intermediate directory: data/data
        self.intermediate_dir = os.path.join(self.extract_to, 'data')

    def tidy(self):
        self._cleanup_existing_pdfs()
        self._extract_archive()
        self._delete_resume_folder()
        self._gather_subdirs()
        self._move_pdfs_to_extract()
        self._cleanup_subdirs()
        self._remove_base_data_dir()
        self._remove_intermediate_data_dir()
        self._print_summary()

    def _cleanup_existing_pdfs(self):
        # Delete any existing PDFs in the extract_to directory
        for fname in os.listdir(self.extract_to):
            if fname.lower().endswith('.pdf'):
                path = os.path.join(self.extract_to, fname)
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _extract_archive(self):
        with zipfile.ZipFile(self.archive_path, 'r') as zf:
            zf.extractall(self.extract_to)

    def _delete_resume_folder(self):
        resume_dir = os.path.join(self.extract_to, 'Resume')
        if os.path.isdir(resume_dir):
            shutil.rmtree(resume_dir)

    def _gather_subdirs(self):
        # Collect all immediate typeN folders under base_data_dir
        for root, dirs, _ in os.walk(self.base_data_dir):
            if os.path.abspath(root) == os.path.abspath(self.base_data_dir):
                self.subdirs.extend(os.path.join(root, d) for d in dirs)

    def _move_pdfs_to_extract(self):
        # Move PDFs from each typeN into top-level extract_to
        for root, _, files in os.walk(self.base_data_dir):
            if os.path.abspath(root) == os.path.abspath(self.base_data_dir):
                continue
            for fname in files:
                if not fname.lower().endswith('.pdf'):
                    continue
                src = os.path.join(root, fname)
                dst = os.path.join(self.extract_to, fname)
                if os.path.exists(dst):
                    self.duplicate_count += 1
                else:
                    shutil.move(src, dst)
                    self.moved_count += 1

    def _cleanup_subdirs(self):
        # Remove each empty typeN folder
        for d in self.subdirs:
            try:
                os.rmdir(d)
            except OSError:
                pass

    def _remove_base_data_dir(self):
        # Remove nested base_data_dir: data/data/data
        try:
            os.rmdir(self.base_data_dir)
        except OSError:
            pass

    def _remove_intermediate_data_dir(self):
        # Remove intermediate directory: data/data
        try:
            os.rmdir(self.intermediate_dir)
        except OSError:
            pass
        
    def _print_summary(self):
        print(f"Moved {self.moved_count} PDFs to '{self.extract_to}'")
        if self.duplicate_count > 0:
            print(f"Skipped {self.duplicate_count} duplicate PDFs")
        else:
            print("No duplicate PDFs found.")