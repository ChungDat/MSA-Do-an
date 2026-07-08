import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .data_processor import load_and_preprocess_data
from .factor_analysis import perform_factor_analysis
from .llm_namer import name_all_factors


class FactorAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.result_data = None
        root.title("Factor Analysis & LLM Naming App")
        root.geometry("800x600")
        self._setup_ui()

    def _setup_ui(self):
        config = ttk.LabelFrame(self.root, text="Cấu hình", padding=10)
        config.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(config, text="Chọn file CSV", command=self.select_file).grid(
            row=0, column=0, padx=5, pady=5
        )
        self.file_label = ttk.Label(config, text="Chưa chọn file")
        self.file_label.grid(row=0, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(config, text="Số nhân tố:").grid(row=1, column=0, sticky=tk.E)
        self.factors_entry = ttk.Entry(config, width=10)
        self.factors_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(config, text="Ngưỡng tải:").grid(row=2, column=0, sticky=tk.E)
        self.threshold_entry = ttk.Entry(config, width=10)
        self.threshold_entry.insert(0, "0.4")
        self.threshold_entry.grid(row=2, column=1, sticky=tk.W, padx=5)

        self.run_button = ttk.Button(
            config, text="Chạy phân tích", command=self.run_analysis
        )
        self.run_button.grid(row=3, column=0, columnspan=4, pady=10)

        result_frame = ttk.LabelFrame(self.root, text="Kết quả", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.result_text = tk.Text(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.save_button = ttk.Button(
            self.root,
            text="Lưu JSON",
            command=self.save_result,
            state=tk.DISABLED,
        )
        self.save_button.pack(anchor=tk.E, padx=15, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Chọn dữ liệu", filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self.file_path = path
            self.file_label.config(text=path)

    def run_analysis(self):
        if not self.file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file CSV.")
            return
        try:
            threshold = float(self.threshold_entry.get())
            value = self.factors_entry.get().strip()
            factors = int(value) if value else None
        except ValueError:
            messagebox.showerror("Lỗi", "Tham số không hợp lệ.")
            return
        self.run_button.config(state=tk.DISABLED)
        threading.Thread(
            target=self._analyze, args=(factors, threshold), daemon=True
        ).start()

    def _analyze(self, factors, threshold):
        try:
            dataframe, names = load_and_preprocess_data(self.file_path)
            groups, _ = perform_factor_analysis(
                dataframe, names, factors, threshold
            )
            self.result_data = name_all_factors(groups)
            self.root.after(0, self._display_results)
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", str(exc)))
        finally:
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))

    def _display_results(self):
        self.result_text.delete("1.0", tk.END)
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

    def save_result(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as output_file:
                json.dump(
                    self.result_data, output_file, ensure_ascii=False, indent=4
                )


def main():
    root = tk.Tk()
    FactorAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
