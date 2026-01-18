from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "library-secret"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["library_db"]
books = db["books"]

# Optional: Ensure _id is the only unique field
# (no more book_id unique index issues)
# books.drop_indexes()  # Uncomment this once if duplicate errors persist

@app.route("/")
def index():
    all_books = list(books.find())
    return render_template("index.html", books=all_books, edit_mode=False, view_mode=False)

@app.route("/add", methods=["POST"])
def add_book():
    title = request.form["title"]
    author = request.form["author"]
    isbn = request.form["isbn"]
    year = request.form["year"]
    copies = request.form["copies"]

    if title:
        books.insert_one({
            "title": title,
            "author": author,
            "isbn": isbn,
            "year": year,
            "copies": int(copies)
        })
        flash("Book added successfully!", "success")
    else:
        flash("Title is required!", "danger")

    return redirect(url_for("index"))

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_book(id):
    book = books.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        year = request.form["year"]
        copies = request.form["copies"]

        books.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "title": title,
                "author": author,
                "isbn": isbn,
                "year": year,
                "copies": int(copies)
            }}
        )
        flash("Book updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("index.html", books=list(books.find()), edit_mode=True, book=book, view_mode=False)

@app.route("/view/<id>")
def view_book(id):
    book = books.find_one({"_id": ObjectId(id)})
    return render_template("index.html", books=list(books.find()), view_mode=True, book=book, edit_mode=False)

@app.route("/delete/<id>")
def delete_book(id):
    books.delete_one({"_id": ObjectId(id)})
    flash("Book deleted successfully!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
