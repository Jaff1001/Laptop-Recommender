import streamlit.web.cli as stcli
import sys
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "app", "main.py")

    sys.argv = ["streamlit", "run", main_script]
    sys.exit(stcli.main())