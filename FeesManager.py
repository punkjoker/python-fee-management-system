from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime

class ClassFees:
    def __init__(self, root, ls, frame_old):
        self.ls = ls
        self.root = root
        self.frame_old = frame_old
        self.Roll_No_var = StringVar()
        self.fees_paid_var = IntVar()
        self.receipt_no_var = StringVar()  # Variable for receipt_no
        self.term_var = StringVar()  # Variable for new term

        # Initialize current term
        self.current_term = self.get_current_term()

        # Creating the main frame.
        self.frame = Frame(root, bg='#163148')
        self.frame.place(x=0, y=0, width=ls[0], height=ls[1])

        # Creating a back button.
        exit_btn = Button(self.frame, text="Back", relief=RAISED, bg='#fbf8e6', command=self.exiting)
        exit_btn.place(x=10, y=10, width=100, height=40)
        
        # Labeling the title
        title = Label(self.frame, text='Manage Student Fees', font=('Algerian', 25, 'bold'), bg='lightgreen')
        title.pack(side=TOP, pady=10)

        # Display current term
        self.current_term = self.get_current_term()
        term_label = Label(self.frame, text=f"Current Term: {self.current_term}", font=("Arial", 14), bg='lightgreen')
        term_label.pack(side=TOP, pady=5)

        # Creating a frame for student list.
        Student_Frame = Frame(self.frame, bd=4, relief=RIDGE, bg='LightBlue')
        Student_Frame.place(x=10, y=100, width=ls[0] - 20, height=ls[1] // 3)

        # Table for displaying student list.
        self.Student_table = ttk.Treeview(Student_Frame, columns=("Roll", "Name", "Class", "Fees Paid", "Fees Due"))
        self.Student_table.heading("Roll", text="Roll No.")
        self.Student_table.heading("Name", text="Name")
        self.Student_table.heading("Class", text="Class")  # Added Class column
        self.Student_table.heading("Fees Paid", text="Fees Paid")
        self.Student_table.heading("Fees Due", text="Fees Due")
        self.Student_table['show'] = 'headings'
        self.Student_table.column("Roll", width=100)
        self.Student_table.column("Name", width=150)
        self.Student_table.column("Class", width=100)  # Column for class
        self.Student_table.column("Fees Paid", width=150)
        self.Student_table.column("Fees Due", width=150)
        self.Student_table.pack(fill=BOTH, expand=1)
        self.Student_table.bind("<ButtonRelease-1>", self.get_cursor)

        # Creating a frame for fee management.
        Manage_Frame = Frame(self.frame, bd=4, relief=RIDGE, bg="cornsilk")
        Manage_Frame.place(x=10, y=ls[1] // 2, width=ls[0] - 20, height=ls[1] // 4)

        # Label and Entry for payment amount.
        lbl_fees = Label(Manage_Frame, text="Enter Payment Amount:", bg="cornsilk", fg="blue", font=("times new roman", 16, "bold"))
        lbl_fees.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        txt_fees = Entry(Manage_Frame, textvariable=self.fees_paid_var, font=("times new roman", 14), bd=5, relief=GROOVE)
        txt_fees.grid(row=0, column=1, pady=10, padx=20, sticky="w")

        # Label and Entry for receipt number.
        lbl_receipt = Label(Manage_Frame, text="Enter Receipt No.:", bg="cornsilk", fg="blue", font=("times new roman", 16, "bold"))
        lbl_receipt.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        txt_receipt = Entry(Manage_Frame, textvariable=self.receipt_no_var, font=("times new roman", 14), bd=5, relief=GROOVE)
        txt_receipt.grid(row=1, column=1, pady=10, padx=20, sticky="w")

        # Submit Payment Button
        submit_btn = Button(Manage_Frame, text="Submit Payment", bg='black', fg='white', width=20, command=self.add_payment)
        submit_btn.grid(row=2, column=0, pady=10, padx=10, sticky="w")

        # View Payment History Button
        view_history_btn = Button(Manage_Frame, text="View Payment History", bg='blue', fg='white', width=20, command=self.view_payment_history)
        view_history_btn.grid(row=2, column=1, pady=10, padx=10, sticky="w")

        # Print Payment History Button
        print_history_btn = Button(Manage_Frame, text="Print STUDENT Payment History", bg='green', fg='white', width=25, command=self.print_payment_history)
        print_history_btn.grid(row=2, column=2, pady=10, padx=10, sticky="w")

        # Print Fee Balances Button
        print_fee_balances_btn = Button(Manage_Frame, text="Print/Save ALL Fee Balances", bg='orange', fg='white', width=25, command=self.print_fee_balances)
        print_fee_balances_btn.grid(row=2, column=3, pady=10, padx=10, sticky="w")

        # Label and Entry for new term
        lbl_term = Label(Manage_Frame, text="Enter New Term:", bg="cornsilk", fg="blue", font=("times new roman", 16, "bold"))
        lbl_term.grid(row=0, column=4, padx=20, pady=20, sticky="w")

        txt_term = Entry(Manage_Frame, textvariable=self.term_var, font=("times new roman", 14), bd=5, relief=GROOVE)
        txt_term.grid(row=0, column=5, pady=20, padx=20, sticky="w")

        # Set New Term Button
        set_term_btn = Button(Manage_Frame, text="Set New Term", bg='purple', fg='white', width=20, command=self.set_new_term)
        set_term_btn.grid(row=2, column=5, pady=10, padx=10, sticky="w")

        # Fetch and display students.
        self.fetch_students()

    def exiting(self):
        """Handle exiting the current frame and showing the previous one."""
        self.frame.destroy()
        self.frame_old.deiconify()

    def get_current_term(self):
        """Retrieve the current term from the database."""
        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()
        cur.execute("SELECT term_name FROM current_term LIMIT 1")
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return 'Term1'  # Default term if not set

    def fetch_students(self):
        """Fetch and display the list of students and their fees for the current term."""
        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()

        # Dynamically generate the table name for the current term
        table_name = f"student_fees_{self.current_term.replace(' ', '_')}"
        print(f"Fetching data from table: {table_name}")  # Debugging line

        try:
            cur.execute(f"""
                SELECT sd.Roll_No, sd.Name, sd.email, 
                       IFNULL(sf.fees_paid, 0) AS fees_paid, 
                       IFNULL(sf.fees_rem, 3500) AS fees_rem
                FROM student_data sd 
                LEFT JOIN {table_name} sf 
                     ON sd.Roll_No = sf.Roll_No
                ORDER BY sd.Name ASC
            """)
            rows = cur.fetchall()
            print("Fetched rows:", rows)  # Debugging line
            self.Student_table.delete(*self.Student_table.get_children())
            for row in rows:
                self.Student_table.insert('', END, values=row)
        except Exception as e:
            print(f"Error fetching students: {e}")  # Error handling
        finally:
            conn.close()

    def get_cursor(self, ev):
        """Handle the event when a student is selected from the list."""
        cursor_row = self.Student_table.focus()
        contents = self.Student_table.item(cursor_row)
        row = contents['values']
        if row:
            self.Roll_No_var.set(row[0])

    def add_payment(self):
        """Add payment for the selected student to the term-specific table."""
        roll_no = self.Roll_No_var.get()
        amount = self.fees_paid_var.get()
        receipt_no = self.receipt_no_var.get()

        if not roll_no:
            messagebox.showerror("Error", "Please select a student to process payment.")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Please enter a valid payment amount.")
            return

        try:
            # Connect to your database
            conn = sqlite3.connect('employee.db')
            cur = conn.cursor()

            # Get the current date for payment record
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Step 1: Insert payment record into the payments table (payment history)
            cur.execute("""
                INSERT INTO payments (Roll_No, payment_amount, payment_date, term, receipt_no)
                VALUES (?, ?, ?, ?, ?)
            """, (roll_no, amount, current_date, self.current_term, receipt_no))

            # Step 2: Update the term-specific fees table
            term_table = f"student_fees_{self.current_term.replace(' ', '_')}"  # e.g., "student_fees_Term_1_2025"
            cur.execute(f"""
                UPDATE {term_table}
                SET fees_paid = fees_paid + ?, fees_rem = fees_rem - ?
                WHERE Roll_No = ?
            """, (amount, amount, roll_no))

            # Commit the changes
            conn.commit()

            # Update the student list to reflect the new fees status
            self.fetch_students()

            messagebox.showinfo("Success", "Payment processed successfully!")
            self.reset_fields()

        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Payment could not be processed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    def reset_fields(self):
        """Reset the input fields after recording payment."""
        self.fees_paid_var.set(0)
        self.receipt_no_var.set('')
        self.Roll_No_var.set('')

    def view_payment_history(self):
        """View the payment history of the selected student."""
        if not self.Roll_No_var.get():
            messagebox.showerror("Error", "Please select a student to view payment history.")
            return
    
        roll_no = self.Roll_No_var.get()
        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()
        cur.execute("""
            SELECT receipt_no, payment_amount, payment_date, term 
            FROM payments 
            WHERE Roll_No = ? 
            ORDER BY payment_date DESC
        """, (roll_no,))
        history = cur.fetchall()
        conn.close()

        # Create a new window to display payment history
        history_window = Toplevel(self.root)
        history_window.title(f"Payment History for {roll_no}")
        history_window.geometry("500x400")

        history_tree = ttk.Treeview(history_window, columns=("Receipt No", "Amount", "Date", "Term"))
        history_tree.heading("Receipt No", text="Receipt No.")
        history_tree.heading("Amount", text="Amount")
        history_tree.heading("Date", text="Date")
        history_tree.heading("Term", text="Term")
        history_tree['show'] = 'headings'
        history_tree.column("Receipt No", width=100)
        history_tree.column("Amount", width=100)
        history_tree.column("Date", width=150)
        history_tree.column("Term", width=100)
        history_tree.pack(fill=BOTH, expand=1)

        for row in history:
            history_tree.insert('', END, values=row)

    def print_payment_history(self):
        """Print or save the payment history of the selected student."""
        if not self.Roll_No_var.get():
            messagebox.showerror("Error", "Please select a student to print payment history.")
            return
    
        roll_no = self.Roll_No_var.get()
        current_term = "Term_1_2025"  # Replace with dynamic term if needed

        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()
        
        # Fetch the student's name using the roll number
        cur.execute("SELECT Name FROM student_data WHERE Roll_No = ?", (roll_no,))
        student_name = cur.fetchone()
        if student_name:
            student_name = student_name[0]
        else:
            messagebox.showerror("Error", "Student name not found.")
            return
        
        # Fetch the payment history from the 'payments' table
        cur.execute("""
            SELECT receipt_no, payment_amount, payment_date, term 
            FROM payments 
            WHERE Roll_No = ? 
            ORDER BY payment_date DESC
        """, (roll_no,))
        history = cur.fetchall()

        # Fetch the current fee balance from the term-specific table
        cur.execute(f"""
            SELECT fees_rem 
            FROM student_fees_{current_term} 
            WHERE Roll_No = ?
        """, (roll_no,))
        balance = cur.fetchone()
    
        conn.close()

        # Ask for the file path to save the history
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(f"Payment History for {student_name} Roll No: {roll_no}\n\n")
                file.write(f"{'Receipt No':<15} {'Payment Amount':<15} {'Payment Date':<20} {'Term':<10}\n")
                file.write("="*70 + "\n")

                for row in history:
                    file.write(f"{row[0]:<15} {row[1]:<15} {row[2]:<20} {row[3]:<10}\n")
            
                if balance:
                    file.write(f"\nCurrent Fee Balance: {balance[0]}\n")
                else:
                    file.write("\nNo balance information available.\n")
        
        messagebox.showinfo("Success", "Payment history saved successfully!")


    def print_fee_balances(self):
        """Print or save the fee balances of all students with fees remaining greater than 1."""
        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()

        # Dynamically generate the table name for the current term
        term_table = f"student_fees_{self.current_term.replace(' ', '_')}"

        # Fetch students with fees remaining greater than 1
        cur.execute(f"""
            SELECT sd.Roll_No, sd.Name, sd.email, sf.fees_paid, sf.fees_rem
            FROM student_data sd 
            LEFT JOIN {term_table} sf ON sd.Roll_No = sf.Roll_No
            WHERE sf.fees_rem > 1
            ORDER BY sd.Name ASC
        """)
        balances = cur.fetchall()
        conn.close()

        # Ask for the file path to save the fee balances
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write("Fee Balances for Students (Fees Due > 1)\n")
                file.write(f"{'Roll No':<15} {'Name':<30} {'Class':<10} {'Fees Paid':<15} {'Fees Due':<15}\n")
                file.write("=" * 75 + "\n")

                for row in balances:
                    file.write(f"{row[0]:<15} {row[1]:<30} {row[2]:<10} {row[3]:<15} {row[4]:<15}\n")
            messagebox.showinfo("Success", "Fee balances saved successfully!")


    def set_new_term(self):
        """Create a new term and reset student fees."""
        new_term = self.term_var.get()
        if not new_term:
            messagebox.showerror("Error", "Please enter a valid term name.")
            return

        conn = sqlite3.connect('employee.db')
        cur = conn.cursor()

        # Create a new table for the current term
        table_name = f"student_fees_{new_term.replace(' ', '_')}"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                Roll_No TEXT PRIMARY KEY,
                fees_paid INTEGER DEFAULT 0,
                fees_rem INTEGER DEFAULT 3500,
                term TEXT
            )
        """)

        # Reset all student fees and populate the new table
        cur.execute("SELECT Roll_No FROM student_data")
        students = cur.fetchall()
        for student in students:
            roll_no = student[0]
            cur.execute(f"""
                INSERT OR REPLACE INTO {table_name} (Roll_No, fees_paid, fees_rem, term) 
                VALUES (?, ?, ?, ?)
            """, (roll_no, 0, 3500, new_term))

        # Update current_term in the database
        cur.execute("DELETE FROM current_term")
        cur.execute("INSERT INTO current_term (term_name) VALUES (?)", (new_term,))

        conn.commit()
        conn.close()

        # Update the current term display
        self.current_term = new_term
        messagebox.showinfo("Success", f"New term '{new_term}' created successfully!")
        self.fetch_students()  # Refresh the student list
        self.reset_fields()  # Reset input fields


    def exiting(self):
        """Handle the action when the 'Back' button is clicked."""
        self.frame.destroy()
        self.frame_old.pack()

def login(root, ls):
    frame = Frame(root, bg='#163148')
    frame.place(x=0, y=0, width=ls[0], height=ls[1])

    Label(frame, text="Login", font=("Arial", 24), bg='#163148', fg='white').pack(pady=50)

    username_var = StringVar()
    password_var = StringVar()

    Label(frame, text="Username:", font=("Arial", 14), bg='#163148', fg='white').pack(pady=10)
    Entry(frame, textvariable=username_var, font=("Arial", 14)).pack(pady=10)

    Label(frame, text="Password:", font=("Arial", 14), bg='#163148', fg='white').pack(pady=10)
    Entry(frame, textvariable=password_var, font=("Arial", 14), show="*").pack(pady=10)

    def attempt_login():
        # In a real application, replace this with actual login validation
        if username_var.get() == "admin" and password_var.get() == "password":
            frame.destroy()
            ClassFees(root, ls, frame)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    Button(frame, text="Login", font=("Arial", 14), command=attempt_login).pack(pady=20)

if __name__ == "__main__":
    root = Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width}x{height}")
    root.title("Fees Management System")

    login(root, (width, height))

    root.mainloop()
