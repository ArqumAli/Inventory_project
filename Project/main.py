import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

DEPARTMENTS = [
    "Accounts", "Admin", "HSE", "Civil", "Coordination", "Dispatch", "Weigh Bridge", "Power Generation", "P.P.C",
    "Production", "Tally Clerk", "Drawing Office", "Diesel Pump", "Electrical", "HR", "Instrument", "Mechanical",
    "Mining", "ITS", "Packing Plant", "QC", "RDF", "WHR", "Logistic", "Time Office", "Main Gate Security",
    "OK Mill CCR", "Main Store",
]

ITEM_DESCRIPTIONS = [
    "Mouse", "Keyboard", "Ethernet Cable", "Power Cable", "Laptop Charger", "Telephone Cable",
]

# Function to initialize the MySQL database
def create_table():
    conn = mysql.connector.connect(
        host="mysql-c7ms",
        user="root",
        password="Arqum@db0336",
        database="inventorydb"
    )
    cursor = conn.cursor()

    # Create the 'inventorylist' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventorytable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            department VARCHAR(50),
            item_description TEXT,
            issued_date DATE,
            crf_number VARCHAR(50),
            remarks TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Function to insert an item into the MySQL database
def insert_item(user_name, department, item_description, issued_date, crf_number, remarks):
    conn = mysql.connector.connect(
        host="mysql-c7ms",
        user="root",
        password="Arqum@db0336",
        database="inventorydb"
    )
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO inventorytable (user_name, department, item_description, issued_date, crf_number, remarks)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_name, department, item_description, issued_date, crf_number, remarks))

    conn.commit()
    conn.close()

# Function to retrieve all items from the MySQL database
def get_all_items():
    conn = mysql.connector.connect(
        host="mysql-c7ms",
        user="root",
        password="Arqum@db0336",
        database="inventorydb"
    )
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM inventorytable')
    items = cursor.fetchall()

    conn.close()

    return items

# Function to update an existing item in the MySQL database
def update_item(item_id, user_name, department, item_description, issued_date, crf_number, remarks):
    conn = mysql.connector.connect(
        host="mysql-c7ms",
        user="root",
        password="Arqum@db0336",
        database="inventorydb"
    )
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE inventorytable
        SET user_name=%s, department=%s, item_description=%s, issued_date=%s, crf_number=%s, remarks=%s
        WHERE id=%s
    ''', (user_name, department, item_description, issued_date, crf_number, remarks, item_id))

    conn.commit()
    conn.close()

# Function to delete an existing item from the MySQL database
def delete_item(item_id):
    conn = mysql.connector.connect(
        host="mysql-c7ms",
        user="root",
        password="Arqum@db0336",
        database="inventorydb"
    )
    cursor = conn.cursor()

    cursor.execute('DELETE FROM inventorytable WHERE id=%s', (item_id,))
    cursor.execute('ALTER TABLE inventorytable AUTO_INCREMENT = 1')

    conn.commit()
    conn.close()

# Main function to run the Streamlit app
def main():
    st.title('Non Asset Item Inventory')

    create_table()  # Create the table if it doesn't exist

    # Sidebar
    st.sidebar.title('Options')
    st.sidebar.markdown("### **Choose an Option**")
    option = st.sidebar.selectbox('', ['View All Entries', 'Create New Entry', 'Update Existing Entries', 'Delete Existing Entry'], index=0)

    if option == 'Create New Entry':
        st.header('Add New Entry')
        item_name = st.text_input('User Name')
        item_department = st.selectbox('Department', DEPARTMENTS)
        item_description = st.multiselect('Item Description', ITEM_DESCRIPTIONS)
        item_issued_date = st.date_input('Issued Date', datetime.today())
        item_crf_number = st.text_input('CRF Number')
        item_remarks = st.text_area('Remarks')

        if st.button('Save Entry'):
            insert_item(
                item_name, item_department, ', '.join(item_description),
                item_issued_date.strftime('%Y-%m-%d'), item_crf_number, item_remarks
            )
            st.success(f'Entry "{item_name}" added successfully!')

    elif option == 'View All Entries':
        st.header('Entry List')
        # Retrieve and display all items
        items = get_all_items()
        if items:
            df = pd.DataFrame(
                items,
                columns=['ID', 'User Name', 'Department', 'Item Description', 'Issued Date', 'CRF Number', 'Remarks']
            )
            st.dataframe(df.style.set_properties(**{'max-height': '700px', 'overflow-y': 'auto'}).set_table_styles([{'selector': 'th', 'props': [('font-size', '30px'), ('font-weight', 'bold')]}]))
        else:
            st.info('No entries in the table.')

    elif option == 'Update Existing Entries':
        st.header('Update Existing Entry')
        # Retrieve and display all items for selection
        items = get_all_items()
        if items:
            item_dict = {item[0]: item[1] for item in items}
            selected_item = st.selectbox('Select Entry to Update', list(item_dict.values()))
            selected_item_id = next((key for key, value in item_dict.items() if value == selected_item), None)

            st.subheader(f"Selected Entry: {selected_item}")
            #st.write(f"Entry ID: {selected_item_id}")

            item_name = st.text_input('User Name', selected_item)
            item_department = st.selectbox('Department', DEPARTMENTS)
            item_description = st.multiselect('Item Description', ITEM_DESCRIPTIONS)
            item_issued_date = st.date_input('Issued Date', datetime.today())
            item_crf_number = st.text_input('CRF Number')
            item_remarks = st.text_area('Remarks')

            if st.button('Update Item'):
                update_item(
                    selected_item_id, item_name, item_department, ', '.join(item_description),
                    item_issued_date.strftime('%Y-%m-%d'), item_crf_number, item_remarks
                )
                st.success(f'Entry "{selected_item}" updated successfully!')

        else:
            st.info('No entries in the table.')

    elif option == 'Delete Existing Entry':
        st.header('Delete Existing Entry')
        # Retrieve and display all items in a table for selection
        items = get_all_items()
        if items:
            df = pd.DataFrame(
                items,
                columns=['ID', 'User Name', 'Department', 'Item Description', 'Issued Date', 'CRF Number', 'Remarks']
            )

            # Make the Issued Date column wider
            df.style.set_properties(**{'width': '400px'}, subset=['Issued Date'])

            st.subheader('Select Entry to Delete:')
            selected_item_id = st.selectbox('', df['ID'].tolist())
            selected_item = df[df['ID'] == selected_item_id].squeeze()

            st.table(pd.DataFrame(selected_item).T)

            if st.button('Delete Entry'):
                delete_item(selected_item_id)
                st.success(f'Entry "{selected_item["Name"]}" deleted successfully!')

        else:
            st.info('No entries in the table.')

if __name__ == '__main__':
    main()
