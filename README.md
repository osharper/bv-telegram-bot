# Beach Volleyball Registration Bot

This project is a Telegram bot designed to manage registrations for beach volleyball sessions. The bot allows users to register for different sessions, view the current registration list, and remove themselves from the list. The bot also supports scheduling registration opening and closing times for different sessions.

## Features

- Register for beach volleyball sessions
- View the current registration list
- Remove yourself from the registration list
- Schedule registration opening and closing times
- Save and load registration data from a local CSV file or an S3 bucket

## Requirements

- Python 3.9
- `python-telegram-bot==20.0`
- `boto3==1.28.0`
- `python-dotenv==1.0.0`

## Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/beach-volleyball-registration-bot.git
   cd beach-volleyball-registration-bot
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory and add the following environment variables:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   USE_S3=true_or_false
   S3_BUCKET_NAME=your_s3_bucket_name
   S3_OBJECT_KEY=your_s3_object_key
   ```

5. Run the bot:
   ```sh
   python main.py
   ```

## Usage

- **/start**: Start the bot and get a welcome message.
- **/add [name]**: Add yourself or the specified name to the registration list.
- **/remove [name]**: Remove yourself or the specified name from the registration list.
- **/list**: View the current registration list.

## Docker

To run the bot using Docker, follow these steps:

1. Build the Docker image:
   ```sh
   docker build -t beach-volleyball-registration-bot .
   ```

2. Run the Docker container:
   ```sh
   docker run --env-file .env beach-volleyball-registration-bot
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [boto3](https://github.com/boto/boto3)
- [python-dotenv](https://github.com/theskumar/python-dotenv)