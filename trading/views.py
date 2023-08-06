from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import os
from django.shortcuts import render, redirect
from .models import Portfolio, Stock
import yfinance as yf
from django.conf import settings
import matplotlib.pyplot as plt 


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('portfolio')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portfolio')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')


@login_required
def portfolio(request):
    user_portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    stocks = Stock.objects.filter(portfolio=user_portfolio)
    return render(request, 'portfolio.html', {'portfolio': user_portfolio, 'stocks': stocks})


@login_required
def buy_stock(request, symbol, quantity):
    user_portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    stock_info = yf.Ticker(symbol)
    current_price = stock_info.history(period='1d').iloc[-1]['Close']
    total_cost = current_price * quantity

    if user_portfolio.balance >= total_cost:
        user_portfolio.balance -= total_cost
        user_portfolio.save()
        user_stock, created = Stock.objects.get_or_create(portfolio=user_portfolio, symbol=symbol)
        if created:
            user_stock.quantity = quantity
        else:
            user_stock.quantity += quantity
        user_stock.save()
        message = "Stock bought successfully!"
    else:
        message = "Insufficient balance to buy the stock."

    return render(request, 'buy.html', {'message': message})


@login_required
def sell_stock(request, symbol, quantity):
    user_portfolio = Portfolio.objects.get(user=request.user)
    user_stock = Stock.objects.get(portfolio=user_portfolio, symbol=symbol)
    
    if user_stock.quantity >= quantity:
        stock_info = yf.Ticker(symbol)
        current_price = stock_info.history(period='1d').iloc[-1]['Close']
        total_gain = current_price * quantity
        user_portfolio.balance += total_gain
        user_portfolio.save()
        user_stock.quantity -= quantity
        if user_stock.quantity == 0:
            user_stock.delete()
        else:
            user_stock.save()
        message = "Stock sold successfully!"
    else:
        message = "You don't own enough quantity of this stock to sell."

    return render(request, 'sell.html', {'message': message})

def show_chart(request, symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='1d')
    data['Close'].plot()
    plt.savefig('static/chart.png')
    return render(request, 'chart.html')

def stock_chart(request):
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 30, 20, 10]

    plt.plot(x, y)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Stock Price Over Time')

    image_path = os.path.join(settings.STATIC_ROOT, 'images', 'plot.png')
    plt.savefig(image_path)

    image_url = os.path.join(settings.STATIC_URL, 'images', 'plot.png')

    return render(request, 'chart.html', {'image_url': image_url})


