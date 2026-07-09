import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .data_processor import (
    calculate_descriptive_statistics,
    load_and_preprocess_data,
)
from .factor_analysis import calculate_eigenvalues, perform_factor_analysis
from .llm_namer import name_all_factors


class FactorAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.statistics_file_path = None
        self.result_data = None
        self.analysis_metadata = None

        root.title("Ứng dụng phân tích dữ liệu")
        root.geometry("900x650")
        self._setup_ui()

    def _setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.factor_tab = ttk.Frame(notebook, padding=5)
        self.statistics_tab = ttk.Frame(notebook, padding=5)
        notebook.add(self.factor_tab, text="Phân tích nhân tố")
        notebook.add(self.statistics_tab, text="Thống kê mô tả")

        self._setup_factor_tab()
        self._setup_statistics_tab()

    def _setup_factor_tab(self):
        config = ttk.LabelFrame(self.factor_tab, text="Cấu hình", padding=10)
        config.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(config, text="Chọn file CSV", command=self.select_file).grid(
            row=0, column=0, padx=5, pady=5
        )
        self.file_label = ttk.Label(config, text="Chưa chọn file")
        self.file_label.grid(row=0, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(config, text="Số nhân tố:").grid(row=1, column=0, sticky=tk.E)
        self.factors_entry = ttk.Entry(config, width=10)
        self.factors_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(
            config,
            text="Để trống: tự chọn tất cả trị riêng > 1 (Kaiser)",
        ).grid(row=1, column=2, columnspan=2, sticky=tk.W)
        ttk.Label(config, text="Ngưỡng tải:").grid(row=2, column=0, sticky=tk.E)
        self.threshold_entry = ttk.Entry(config, width=10)
        self.threshold_entry.insert(0, "0.4")
        self.threshold_entry.grid(row=2, column=1, sticky=tk.W, padx=5)

        self.run_button = ttk.Button(
            config, text="Chạy phân tích", command=self.run_analysis
        )
        self.run_button.grid(row=3, column=0, columnspan=4, pady=10)

        result_frame = ttk.LabelFrame(
            self.factor_tab, text="Kết quả", padding=10
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text = tk.Text(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.save_button = ttk.Button(
            self.factor_tab,
            text="Lưu JSON",
            command=self.save_result,
            state=tk.DISABLED,
        )
        self.save_button.pack(anchor=tk.E, padx=10, pady=5)

    def _setup_statistics_tab(self):
        controls = ttk.LabelFrame(
            self.statistics_tab, text="Dữ liệu đầu vào", padding=10
        )
        controls.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(
            controls,
            text="Chọn file CSV",
            command=self.select_statistics_file,
        ).grid(row=0, column=0, padx=5, pady=5)
        self.statistics_file_label = ttk.Label(
            controls, text="Chưa chọn file"
        )
        self.statistics_file_label.grid(row=0, column=1, sticky=tk.W)
        controls.columnconfigure(1, weight=1)

        self.statistics_button = ttk.Button(
            controls,
            text="Tính các đại lượng",
            command=self.run_statistics,
        )
        self.statistics_button.grid(row=1, column=0, columnspan=2, pady=10)

        result_frame = ttk.LabelFrame(
            self.statistics_tab, text="Kết quả thống kê", padding=10
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        self.statistics_text = tk.Text(
            result_frame, wrap=tk.NONE, font=("Consolas", 10)
        )
        vertical_scroll = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.statistics_text.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            result_frame,
            orient=tk.HORIZONTAL,
            command=self.statistics_text.xview,
        )
        self.statistics_text.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )
        self.statistics_text.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

    def select_file(self):
        path = self._ask_for_csv()
        if path:
            self.file_path = path
            self.file_label.config(text=path)

    def select_statistics_file(self):
        path = self._ask_for_csv()
        if path:
            self.statistics_file_path = path
            self.statistics_file_label.config(text=path)

    @staticmethod
    def _ask_for_csv():
        return filedialog.askopenfilename(
            title="Select data", filetypes=[("CSV files", "*.csv")]
        )

    def run_analysis(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a CSV file.")
            return
        try:
            threshold = float(self.threshold_entry.get())
            value = self.factors_entry.get().strip()
            factors = int(value) if value else None
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid parameters. Enter a whole number of factors "
                "and a numeric loading threshold.",
            )
            return

        self.run_button.config(state=tk.DISABLED)
        threading.Thread(
            target=self._analyze, args=(factors, threshold), daemon=True
        ).start()

    def _analyze(self, factors, threshold):
        try:
            dataframe, names = load_and_preprocess_data(self.file_path)
            eigenvalues = calculate_eigenvalues(dataframe)
            groups, extracted = perform_factor_analysis(
                dataframe, names, factors, threshold
            )
            self.analysis_metadata = {
                "automatic": factors is None,
                "extracted": extracted,
                "eigenvalues": eigenvalues.tolist(),
            }
            self.result_data = name_all_factors(groups)
            self.root.after(0, self._display_results)
        except Exception as exc:
            error = str(exc)
            self.root.after(
                0, lambda: messagebox.showerror("Error", error)
            )
        finally:
            self.root.after(
                0, lambda: self.run_button.config(state=tk.NORMAL)
            )

    def run_statistics(self):
        if not self.statistics_file_path:
            messagebox.showerror("Error", "Please select a CSV file.")
            return

        self.statistics_button.config(state=tk.DISABLED)
        self.statistics_text.delete("1.0", tk.END)
        self.statistics_text.insert(tk.END, "Calculating...")
        threading.Thread(target=self._calculate_statistics, daemon=True).start()

    def _calculate_statistics(self):
        try:
            summary, covariance = calculate_descriptive_statistics(
                self.statistics_file_path
            )
            output = (
                "DESCRIPTIVE STATISTICS\n"
                "======================\n"
                f"{summary.to_string(float_format=lambda x: f'{x:.6f}')}\n\n"
                "SAMPLE COVARIANCE MATRIX\n"
                "========================\n"
                f"{covariance.to_string(float_format=lambda x: f'{x:.6f}')}"
            )
            self.root.after(0, lambda: self._show_statistics(output))
        except Exception as exc:
            error = str(exc)
            self.root.after(
                0, lambda: messagebox.showerror("Error", error)
            )
        finally:
            self.root.after(
                0, lambda: self.statistics_button.config(state=tk.NORMAL)
            )

    def _show_statistics(self, output):
        self.statistics_text.delete("1.0", tk.END)
        self.statistics_text.insert(tk.END, output)

    def _display_results(self):
        self.result_text.delete("1.0", tk.END)
        metadata = self.analysis_metadata or {}
        if metadata.get("automatic"):
            eigenvalues = metadata.get("eigenvalues", [])
            selected = [value for value in eigenvalues if value > 1]
            self.result_text.insert(
                tk.END,
                "AUTOMATIC SELECTION USING THE KAISER CRITERION\n"
                f"Eigenvalues: {', '.join(f'{value:.4f}' for value in eigenvalues)}\n"
                f"Eigenvalues > 1: {', '.join(f'{value:.4f}' for value in selected)}\n"
                f"Selected factors: {metadata.get('extracted', 1)}\n\n",
            )
        for factor, data in self.result_data.items():
            self.result_text.insert(
                tk.END,
                f"[{factor}] → {data['llm_name']}\n"
                f"{data['explanation']}\n"
                + "\n".join(
                    f"  - {item['feature']} ({item['loading']:.4f})"
                    for item in data["features"]
                )
                + "\n\n",
            )
        self.save_button.config(state=tk.NORMAL)
        messagebox.showinfo(
            "Analysis Complete",
            "Analysis completed successfully.",
        )

    def save_result(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as output_file:
                json.dump(
                    self.result_data, output_file, ensure_ascii=False, indent=4
                )
            messagebox.showinfo(
                "Save Complete",
                "The analysis result was saved successfully.",
            )


def main():
    root = tk.Tk()
    FactorAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
