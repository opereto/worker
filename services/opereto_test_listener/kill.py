from run import ServiceRunner

if __name__ == "__main__":
    sr = ServiceRunner()
    sr._print_step_title('Terminating task listener process..')
    exit(sr.teardown())
