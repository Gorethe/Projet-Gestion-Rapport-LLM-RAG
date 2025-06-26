import psycopg2

# Configuration (à garder synchrone avec le script principal)
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "collections"
DB_USER = "christine"
DB_PASS = "123456789"

def clear_database():
    """Vide complètement la table tb_vecteurs avec confirmation"""
    conn = None
    cursor = None
    try:
        confirm = input(" Vider TOUTE la base de données ? (y/n): ")
        if confirm.lower() != 'y':
            print("Annulation de la suppression")
            return

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        
        cursor.execute("TRUNCATE TABLE tb_vecteurs RESTART IDENTITY CASCADE")
        conn.commit()
        print("Base de données vidée avec succès")
        
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors du vidage : {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()