from connect_db import get_db_connection

def submit_review(product_id, username, rating, comment=None):
    """
    Allows a customer to submit a new review for a product.

    Args:
        product_id (int): ID of the product.
        username (str): Customer's username.
        rating (int): Rating between 1 to 5.
        comment (str): Optional review comment.

    Returns:
        dict: Success or error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Reviews (ProductID, CustomerUsername, Rating, Comment)
        VALUES (?, ?, ?, ?)
    ''', (product_id, username, rating, comment))

    conn.commit()
    conn.close()
    return {"message": "Review submitted successfully."}

def update_review(review_id, rating=None, comment=None):
    """
    Updates an existing review with a new rating or comment.

    Args:
        review_id (int): ID of the review.
        rating (int, optional): Updated rating.
        comment (str, optional): Updated comment.

    Returns:
        dict: Success or error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    values = []
    if rating is not None:
        updates.append("Rating = ?")
        values.append(rating)
    if comment is not None:
        updates.append("Comment = ?")
        values.append(comment)

    if not updates:
        return {"error": "No fields to update."}

    values.append(review_id)
    cursor.execute(f'''
        UPDATE Reviews
        SET {', '.join(updates)}, Timestamp = CURRENT_TIMESTAMP
        WHERE ReviewID = ?
    ''', values)

    conn.commit()
    conn.close()
    return {"message": "Review updated successfully."}


def get_review_by_id(review_id):
    """
    Fetches a review by its ID.

    Args:
        review_id (int): ID of the review.

    Returns:
        dict: The review details or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ReviewID, ProductID, CustomerUsername, Rating, Comment FROM Reviews WHERE ReviewID = ?', (review_id,))
    review = cursor.fetchone()
    conn.close()
    return dict(review) if review else None

def delete_review(review_id):
    """
    Deletes a specific review.

    Args:
        review_id (int): ID of the review.

    Returns:
        dict: Success or error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Reviews WHERE ReviewID = ?', (review_id,))
    conn.commit()
    conn.close()
    return {"message": "Review deleted successfully."}


def get_product_reviews(product_id):
    """
    Retrieves all reviews for a specific product.

    Args:
        product_id (int): ID of the product.

    Returns:
        list: List of reviews for the product.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ReviewID, CustomerUsername, Rating, Comment, Timestamp
        FROM Reviews
        WHERE ProductID = ? AND Status IN ('Pending', 'Approved')
        ORDER BY Timestamp DESC
    ''', (product_id,))
    reviews = cursor.fetchall()
    conn.close()
    return [dict(review) for review in reviews]



def get_customer_reviews(username):
    """
    Retrieves all reviews submitted by a specific customer.

    Args:
        username (str): Customer's username.

    Returns:
        list: List of reviews submitted by the customer.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ReviewID, ProductID, Rating, Comment, Timestamp
        FROM Reviews
        WHERE CustomerUsername = ? AND Status IN ('Pending', 'Approved')
        ORDER BY Timestamp DESC
    ''', (username,))
    reviews = cursor.fetchall()
    conn.close()
    return [dict(review) for review in reviews]


def moderate_review(review_id, status):
    """
    Moderates a review by updating its status.

    Args:
        review_id (int): ID of the review.
        status (str): New status ('Approved' or 'Flagged').

    Returns:
        dict: Success or error message.
    """
    if status not in ['Approved', 'Flagged']:
        return {"error": "Invalid status."}

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Reviews
        SET Status = ?
        WHERE ReviewID = ?
    ''', (status, review_id))

    conn.commit()
    conn.close()
    return {"message": f"Review status updated to '{status}'."}


def get_review_details(review_id):
    """
    Retrieves detailed information for a specific review.

    Args:
        review_id (int): ID of the review.

    Returns:
        dict: Review details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ProductID, CustomerUsername, Rating, Comment, Timestamp
        FROM Reviews
        WHERE ReviewID = ? AND Status IN ('Pending', 'Approved')
    ''', (review_id,))
    review = cursor.fetchone()
    conn.close()
    return dict(review) if review else None
