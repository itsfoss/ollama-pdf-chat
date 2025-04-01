import os
import sys
import asyncio

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set up asyncio policy for Windows if needed
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Run the Streamlit app
if __name__ == '__main__':
    os.system(f"streamlit run {os.path.join(src_path, 'streamlit_app.py')}")
