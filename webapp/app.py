from flask import Flask, request, jsonify, render_template, abort
import hmac
import hashlib
import os
import json
from urllib.parse import unquote
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env') # Look for .env in the parent directory

app = Flask(__name__, template_folder='templates')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    # In a real app, you might want to handle this more gracefully
    # For this example, we exit if the token is missing on startup
    exit()

def validate_init_data(init_data_str: str, bot_token: str) -> tuple[bool, dict | None]:
    """Validates the initData string received from Telegram WebApp.

    Args:
        init_data_str: The raw initData string.
        bot_token: The Telegram bot token.

    Returns:
        A tuple containing:
        - bool: True if validation is successful, False otherwise.
        - dict | None: Parsed user data if validation is successful, None otherwise.
    """
    try:
        # URL Decode the string first
        init_data_str = unquote(init_data_str)

        # Split into key-value pairs
        params = dict(pair.split('=', 1) for pair in init_data_str.split('&'))

        # Extract the hash and remove it from params for validation
        received_hash = params.pop('hash', None)
        if not received_hash:
            logger.warning("Hash not found in initData")
            return False, None

        # Sort keys alphabetically
        sorted_keys = sorted(params.keys())
        # Construct the data-check-string
        data_check_string = "\n".join(f"{key}={params[key]}" for key in sorted_keys)

        # Calculate the secret key
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

        # Calculate the comparison hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Compare hashes
        if calculated_hash == received_hash:
            logger.info("initData validation successful.")
            # Parse user data if validation is successful
            user_data = params.get('user')
            if user_data:
                try:
                    return True, json.loads(user_data)
                except json.JSONDecodeError:
                    logger.error("Failed to decode user JSON from initData.")
                    return True, None # Valid hash, but user data is malformed
            return True, None # Valid hash, but no user data found
        else:
            logger.warning(f"initData validation failed. Received hash: {received_hash}, Calculated hash: {calculated_hash}")
            return False, None

    except Exception as e:
        logger.error(f"Error during initData validation: {e}", exc_info=True)
        return False, None

@app.route('/')
def index():
    """Serves the main HTML page for the WebApp."""
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_data():
    """Receives initData from frontend and validates it."""
    data = request.json
    init_data = data.get('initData')

    # --- DEBUGGING: Print received initData --- 
    # WARNING: This logs sensitive user information and the validation hash.
    # DO NOT use this logging level in production environments.
    # It's included here solely for demonstration/debugging purposes.
    print("\n--- DEBUG START: Received initData ---")
    print(f"Raw initData string: {init_data}")
    print("--- WARNING: Above data is sensitive. Do not log in production! ---")
    print("--- DEBUG END: Received initData ---\n")
    # --- END DEBUGGING ---

    if not init_data:
        logger.warning("Received validation request with no initData.")
        return jsonify({'status': 'error', 'message': 'Missing initData'}), 400

    logger.info("Received initData for validation. Proceeding with validation...") # Changed log message slightly
    is_valid, user_info = validate_init_data(init_data, BOT_TOKEN)

    if is_valid:
        # logger.info(f"Validation successful. User Info: {user_info}") # Avoid logging user info by default
        logger.info("Validation successful.") # Simplified log
        # Here you would typically create a session for the user,
        # store user info in your database, etc.
        return jsonify({
            'status': 'success',
            'message': 'Authentication successful!',
            'user_info': user_info
        })
    else:
        logger.warning("Validation failed.")
        # Use abort(403) for a standard Forbidden response
        abort(403, description="Invalid initData: Authentication failed.")


# Custom error handler for 403 Forbidden
@app.errorhandler(403)
def forbidden(e):
    response = jsonify(status='error', message=str(e.description))
    response.status_code = 403
    return response

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on the network (e.g., for ngrok)
    # Use a port like 5001 to avoid conflicts if other services run on 5000
    # Turn off debug mode for production/security
    app.run(host='0.0.0.0', port=5001, debug=False) 