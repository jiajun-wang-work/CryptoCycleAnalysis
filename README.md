# Crypto Cycle Analysis Dashboard

A professional cryptocurrency cycle analysis tool built with Streamlit, helping investors analyze market cycles relative to Bitcoin halving events.

## Features
- **Dashboard**: Real-time price, cycle progress, and recent trends.
- **Cycle Analysis**: Historical data visualization anchored to BTC halving dates (Log/Linear scales).
- **Price Prediction**: Fan charts projecting future price ranges based on historical cycle performance.
- **DCA Calculator**: Backtest Dollar Cost Averaging strategies.
- **Multi-language Support**: English, Chinese, Japanese.

## How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

## How to Deploy to Public Internet (Streamlit Community Cloud)

The easiest way to publish this website for free is using **Streamlit Community Cloud**.

### Step 1: Push code to GitHub
1. Create a new repository on GitHub.
2. Push all files in this folder to the repository.
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository (`<your-repo-name>`), branch (`main`), and main file path (`app.py`).
4. Click **"Deploy!"**.

### Step 3: Configure Secrets (Optional)
If you want to use a CoinGecko API Key (to avoid rate limits):
1. In your deployed app dashboard, click "Settings" -> "Secrets".
2. Add your API key like this:
   ```toml
   # .streamlit/secrets.toml
   api_key = "YOUR_COINGECKO_API_KEY"
   ```
   *Note: The app code currently accepts API Key via the Sidebar input, so this step is optional unless you modify the code to read from secrets.*

## Data Sources
- **CoinGecko**: Primary data source (Best quality).
- **Yahoo Finance**: Fallback source (Free, long history).
- **Binance**: Recent price data.
- **Local Data**: Custom historical data for ETH (2015-2017).

## Author
**JW** - Crypto Cycle Analyst
