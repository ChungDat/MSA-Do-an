import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import threading

from data_processor import load_and_preprocess_data
from factor_analysis import perform_factor_analysis
from llm_namer import name_all_factors

class FactorAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factor Analysis & LLM Naming App")
        self.root.geometry("800x600")
        
        self.file_path = None
        self.result_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame Configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration Parameters", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Select file
        ttk.Button(config_frame, text="Select CSV File", command=self.select_file).grid(row=0, column=0, padx=5, pady=5)
        self.lbl_file = ttk.Label(config_frame, text="No file selected")
        self.lbl_file.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=5)
        
        # Number of factors
        ttk.Label(config_frame, text="Number of factors:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.entry_factors = ttk.Entry(config_frame, width=10)
        self.entry_factors.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(config_frame, text="(Leave empty = Auto via Eigenvalue > 1)").grid(row=1, column=2, sticky=tk.W)
        
        # Loading threshold
        ttk.Label(config_frame, text="Loading Threshold:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.entry_threshold = ttk.Entry(config_frame, width=10)
        self.entry_threshold.insert(0, "0.4")
        self.entry_threshold.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Run button
        self.btn_run = ttk.Button(config_frame, text="Run Analysis", command=self.run_analysis)
        self.btn_run.grid(row=3, column=0, columnspan=4, pady=10)
        
        # Frame Results
        result_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.text_result = tk.Text(result_frame, wrap=tk.WORD)
        self.text_result.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(result_frame, command=self.text_result.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_result.config(yscrollcommand=scrollbar.set)
        
        # Frame Action buttons
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X)
        
        self.btn_save = ttk.Button(action_frame, text="Save Results (JSON)", command=self.save_result, state=tk.DISABLED)
        self.btn_save.pack(side=tk.RIGHT, padx=10)
        
    def select_file(self):
        filetypes = (('CSV files', '*.csv'), ('All files', '*.*'))
        filepath = filedialog.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
        if filepath:
            self.file_path = filepath
            self.lbl_file.config(text=filepath)
            
    def run_analysis(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
            
        factors_str = self.entry_factors.get()
        n_factors = int(factors_str) if factors_str.isdigit() and int(factors_str) > 0 else None
        
        try:
            threshold = float(self.entry_threshold.get())
        except ValueError:
            messagebox.showerror("Error", "Loading threshold must be a float.")
            return
            
        self.btn_run.config(state=tk.DISABLED)
        self.text_result.delete('1.0', tk.END)
        self.text_result.insert(tk.END, "Processing data...\n")
        
        # Run logic in separate thread to prevent GUI blocking
        thread = threading.Thread(target=self._analysis_task, args=(n_factors, threshold))
        thread.daemon = True
        thread.start()
        
    def _analysis_task(self, n_factors, threshold):
        try:
            # 1. Preprocess
            df_scaled, feature_names = load_and_preprocess_data(self.file_path)
            self._update_text(f"Loaded {df_scaled.shape[0]} rows and {df_scaled.shape[1]} features.\n")
            
            # 2. Factor Analysis
            self._update_text("Analyzing factors...\n")
            factor_groupings, extracted = perform_factor_analysis(
                df_scaled, feature_names, n_factors, threshold
            )
            self._update_text(f"Extracted {extracted} factors.\n")
            
            # 3. LLM Naming
            self._update_text("Calling LLM for semantic analysis (this may take time)...\n")
            self.result_data = name_all_factors(factor_groupings)
            
            self._update_text("\n--- COMPLETED ---\n\n")
            self._display_results()
            
            self.root.after(0, lambda: self.btn_save.config(state=tk.NORMAL))
            
        except Exception as e:
            self._update_text(f"\n[ERROR]: {str(e)}\n")
            
        finally:
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL))
            
    def _update_text(self, text):
        self.root.after(0, self._insert_text, text)
        
    def _insert_text(self, text):
        self.text_result.insert(tk.END, text)
        self.text_result.see(tk.END)
        
    def _display_results(self):
        if not self.result_data:
            return
            
        text = ""
        for original_name, data in self.result_data.items():
            text += f"[{original_name}] -> New Name: {data['llm_name']}\n"
            text += f"Explanation: {data['explanation']}\n"
            text += "Component features:\n"
            for feature in data['features']:
                text += f"  - {feature['feature']} (Loading: {feature['loading']:.4f})\n"
            text += "-" * 40 + "\n"
            
        self._update_text(text)
        
    def save_result(self):
        if not self.result_data:
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save analysis results"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.result_data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", f"Results saved at:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FactorAnalysisApp(root)
    root.mainloop()
