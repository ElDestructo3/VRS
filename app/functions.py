from fpdf import FPDF
from app.models import User, Movie, Order
from app import db
from time import time
from flask import flash

def purchase_movie(user_id, movie_id, qty):
    try:
        #get movie details
        user_obj = User.query.filter_by(id=user_id).first() #sure to exist
        movie_obj = Movie.query.filter_by(id=movie_id).first()

        if movie_obj is not None:    
            #check for funds, and stock, and existence of movie
            if user_obj.balance < movie_obj.price :
                raise ValueError("Insufficient Balance")
            elif movie_obj.qty < qty :
                raise ValueError("Insufficient Quantity in Stock")
            else:
                my_order = Order(user_id = user_obj.id, movie_id = movie_id, timestamp = time(),
                status="NO", price = movie_obj.price, quantity = qty)
                movie_obj.qty -= qty
                db.session.add(my_order)
                db.session.commit()
                flash('Congratulations. Purchase Successful')
        else:
            raise ValueError("Movie Not Found!")

    except ValueError as e:
        print(e)

def generate_receipt(movie_id):
    try:
        order_obj = Order.query.filter_by(id=movie_id).first()

        if order_obj is not None:
            receipt = FPDF()
            receipt.add_page()
            receipt.set_font('Arial', 'B', 16)
            receipt.cell(200, 10, 'Movie Rentals', 0, 1, 'C')
            receipt.set_font('Arial', '', 12)
            receipt.cell(200, 10, 'Order ID: {}'.format(order_obj.id), 0, 1, 'C')
            receipt.cell(200, 10, txt=f"Movie ID: {order_obj.movie_id}", ln=1, align="C")
            receipt.cell(200, 10, txt=f"Customer ID: {order_obj.user_id}", ln=1, align="C")
            receipt.cell(200, 10, txt=f"Total Price: {order_obj.price}", ln=1, align="C")
            receipt.cell(200, 10, txt=f" Date: {order_obj.timestamp}", ln=1, align="C")
            #receipt.cell(200, 10, txt=f"End Date: {order_obj.endDate}", ln=1, align="C")
            receipt.cell(200, 10, txt=f"Order Status: {order_obj.status}", ln=1, align="C")
            receipt.output("receipt" + str(order_obj.id)+".pdf")
        
        else:
            raise KeyError("Order Not Found!")
    except KeyError as e:
        print(e)

def view_balance(user_id):
    try:
        user_obj = Order.query.filter_by(id=user_id).first()

        if user_obj is not None:
            if (user_obj.user_cat == 'user'):
                if not user_obj.balance:
                    user_obj.balance = 0
                print('Your balance is Rs. {}'.format(user_obj.balance))
        
            else:
                print('Applicable for users only.')
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        print(e)

def add_balance(user_id, amount):
    try:
        user_obj = Order.query.filter_by(id=user_id).first()

        if user_obj is not None:
            if (user_obj.user_cat == 'user'):
                if not user_obj.balance:
                    user_obj.balance = 0
                try:
                    if amount<0:
                        raise ValueError("Amount cannot be negative.")
                    else:
                        user_obj.balance = amount + user_obj.balance
                except ValueError as v:
                    print(v)
                    
                print("Amount added successfully. Your new balance is Rs. {}".format(user_obj.balance))
        
            else:
                print('Applicable for users only.')
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        print(e)

def returnMovie( order_id):
    try:
        
        order_obj = Order.query.filter_by(id=order_id).first()

        if order_obj is not None:
            if order_obj.status == "YES":
                raise ValueError("Movie already returned.")
            else:
                order_obj.status = "YES"
                db.session.commit()
                print("Movie returned successfully.")
        else:
            raise ValueError("Order Not Found!")

    except ValueError as e:
        print(e)

def view_orders(user_id):
    try:
        user_obj = Order.query.filter_by(id=user_id).first()

        if user_obj is not None:
            if (user_obj.user_cat == 'user'):
                
                print('Your orders are:')
                for order in Order.query.filter_by(user_id=user_id):
                    print(order.id)
                    print(order.movie_id)
                    print(order.price)
                    print(order.timestamp)
                    print(order.status)
                    print("\n")
        
            else:
                print('Applicable for users only.')
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        print(e)

def view_deadlines(user_id):
    try:
        user_obj = Order.query.filter_by(id=user_id).first()

        if user_obj is not None:
            if (user_obj.user_cat == 'user'):
                
                print('Your deadlines are:')
                for order in Order.query.filter_by(user_id=user_id):
                    if order.status == "NO":
                        print(order.id)
                        print(order.movie_id)
                        print(order.price)
                        print(order.timestamp)
                        print(order.status)
                        print("\n")
        
            else:
                print('Applicable for users only.')
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        print(e)


def restock_movies(movie_id, quantity, user_id):
    try:

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
    except ValueError as e:
        print(e)
    try:
        movie_obj = Movie.query.filter_by(id=movie_id).first()
        user_obj = Order.query.filter_by(id=user_id).first()
        if user_obj.user_cat == 'staff':
            if movie_obj is not None:
                movie_obj.qty += quantity
                db.session.commit()
                print("Movie restocked successfully.")
            else:
                raise ValueError("Movie Not Found!")
        else:
            raise ValueError("Only staff can restock movies.")

    except ValueError as e:
        print(e)

def search_movies(keyword):
    for movie in Movie.query.order_by(Movie.name):
        if keyword in movie.name or keyword in movie.genre or keyword in movie.description:
            print(movie.id)
            print(movie.name)
            print(movie.genre)
            print(movie.price)
            print(movie.qty)
            print("\n")
    print("Search complete.")
    