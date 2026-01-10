# Stock Vault

<br>

Stock Vault is designed to provide a secure and user-friendly platform for managing and tracking stock portfolios. The project aims to offer a comprehensive tool for users to monitor their investments, access real-time stock data, and organize their financial assets efficiently, catering to both novice and experienced investors.

The Stock Vault system includes features like portfolio tracking, real-time market data integration, and personalized insights to help users make informed investment decisions. It adopts a streamlined approach, enabling users to visualize their financial performance and optimize their strategies. The platform facilitates online access for convenient, self-paced portfolio management, fostering an engaging environment to maximize investment potential and boost confidence in financial planning.

## Getting Started

If you are new to the project, here are some initial steps to get started:

**1. Clone the project**

```
git clone https://github.com/ghanteyyy/StockVault.git
```

**2. Install Dependencies**

```
pip install -r requirements.txt
```

**3. Configure Database**

```
python manage.py makemigrations
```

```
python manage.py migrate
```

**4. Run the server**

```
python manage.py runserver
```

**5. Open following URL in your web browser**

```
127.0.0.1:8000/
```

## Optional Database Configurations

The following configurations are necessary solely for the purpose of generating dummy data for testing.
<br><br>
**1. Populate Stocks**

```
python manage.py PopulateStocks
```

**2. Populate Users**

```
python manage.py PopulateUsers
```

**3. Populate Portfolios for respective user**

```
python manage.py PopulatePortfolios
```

## Technologies Used

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Django
- **Database:** PostgreSQL
