# import subprocess, sys
#
# p = subprocess.Popen(["powershell.exe",
#               # "C:\\Users\\USER\\Desktop\\helloworld.ps1"],
#               "C:\Program Files\WindowsPowerShell\Modules\PDFForm\PdfForm.ps1"],
#               stdout=sys.stdout)
# p.communicate()

import sys
import subprocess


def main():
    # cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File", ".\\script00.ps1"]  # Specify relative or absolute path to the script
    cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File", "C:\Program Files\WindowsPowerShell\Modules\PDFForm\PdfForm.ps1"]
    ec = subprocess.call(cmd)
    print("Powershell returned: {0:d}".format(ec))


if __name__ == "__main__":
    print("Python {0:s} {1:d}bit on {2:s}\n".format(" ".join(item.strip() for item in sys.version.split("\n")), 64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    main()
    print("\nDone.")
