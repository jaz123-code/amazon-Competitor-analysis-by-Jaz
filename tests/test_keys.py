# Ensure the project root is on sys.path so we can import main
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import render_product_card

# This is a lightweight smoke test to ensure render_product_card can be called
# with index without raising exceptions. It won't run Streamlit UI.

def test_render_calls():
    products = [
        {"asin": "A1", "title": "Product A"},
        {"asin": "A1", "title": "Product A duplicate"},
        {"asin": "B2", "title": "Product B"},
    ]
    # Call render_product_card for each product with indices
    for i, p in enumerate(products):
        # We expect no exceptions when calling the function (Streamlit may try to render)
        try:
            render_product_card(p, index=i)
        except Exception as e:
            print('Error when rendering product', p['asin'], e)
            raise
    print('render_product_card calls completed successfully')

if __name__ == '__main__':
    test_render_calls()
