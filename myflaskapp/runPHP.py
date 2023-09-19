import subprocess
import signal
import time

class RunPHP:

    def __init__(self, php_string):
        self.output = "Init"
        self.output = self.run_php_script(php_string, 1)


    def run_php_script(self, php_code, timeout_seconds):
        try:
            # Start the PHP process with the code as input
            process = subprocess.Popen(['php'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Write the PHP code to the process's stdin
            process.stdin.write(php_code)
            process.stdin.close()

            # Wait for the process to finish or timeout
            start_time = time.time()
            while True:
                return_code = process.poll()
                if return_code is not None:
                    break

                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    # If the process runs longer than the allowed timeout, kill it
                    process.terminate()
                    print("PHP code timeout")
                    return "PHP code timeout"

            # Capture the output of the PHP code
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print("PHP code OK")
                return stdout
            else:
                print("PHP code error")
                return stderr
        except Exception as e:
            print("An error occurred while running the PHP code")
            return (str(e))

        return