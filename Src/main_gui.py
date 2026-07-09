import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .data_processor import (
    calculate_descriptive_statistics,
    load_and_preprocess_data,
)
from .factor_analysis import (
    calculate_eigenvalues,
    determine_scree_elbow,
    parallel_analysis,
    perform_factor_analysis,
)
from .llm_namer import name_all_factors


class FactorAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.statistics_file_path = None
        self.result_data = None
        self.analysis_metadata = None
        self.factor_count_file_path = None

        root.title("Ứng dụng phân tích dữ liệu")
        root.geometry("900x650")
        self._setup_ui()

    def _setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.factor_tab = ttk.Frame(notebook, padding=5)
        self.statistics_tab = ttk.Frame(notebook, padding=5)
        self.factor_count_tab = ttk.Frame(notebook, padding=5)
        notebook.add(self.factor_tab, text="Phân tích nhân tố")
        notebook.add(self.statistics_tab, text="Thống kê mô tả")
        notebook.add(self.factor_count_tab, text="Xác định số nhân tố")

        self._setup_factor_tab()
        self._setup_statistics_tab()
        self._setup_factor_count_tab()

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

    def _setup_factor_count_tab(self):
        controls = ttk.LabelFrame(
            self.factor_count_tab, text="Dữ liệu đầu vào", padding=10
        )
        controls.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(
            controls, text="Chọn file CSV", command=self.select_factor_count_file
        ).grid(row=0, column=0, padx=5, pady=5)
        self.factor_count_file_label = ttk.Label(controls, text="Chưa chọn file")
        self.factor_count_file_label.grid(row=0, column=1, sticky=tk.W)
        controls.columnconfigure(1, weight=1)
        self.factor_count_button = ttk.Button(
            controls, text="Xác định số nhân tố", command=self.run_factor_count
        )
        self.factor_count_button.grid(row=1, column=0, columnspan=2, pady=8)

        content = ttk.Panedwindow(self.factor_count_tab, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_frame = ttk.LabelFrame(content, text="Kết luận", padding=8)
        plot_frame = ttk.LabelFrame(content, text="Scree Plot", padding=8)
        content.add(text_frame, weight=1)
        content.add(plot_frame, weight=1)
        self.factor_count_text = tk.Text(text_frame, wrap=tk.WORD, width=48)
        self.factor_count_text.pack(fill=tk.BOTH, expand=True)

        self.scree_figure = Figure(figsize=(5, 4), dpi=100)
        self.scree_axis = self.scree_figure.add_subplot(111)
        self.scree_canvas = FigureCanvasTkAgg(self.scree_figure, master=plot_frame)
        self.scree_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_scree([])

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

    def select_factor_count_file(self):
        path = self._ask_for_csv()
        if path:
            self.factor_count_file_path = path
            self.factor_count_file_label.config(text=path)

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

    def run_factor_count(self):
        if not self.factor_count_file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn một file CSV.")
            return
        self.factor_count_button.config(state=tk.DISABLED)
        self.factor_count_text.delete("1.0", tk.END)
        self.factor_count_text.insert(tk.END, "Đang tính toán...")
        threading.Thread(target=self._calculate_factor_count, daemon=True).start()

    def _calculate_factor_count(self):
        try:
            dataframe, _ = load_and_preprocess_data(self.factor_count_file_path)
            eigenvalues = calculate_eigenvalues(dataframe)
            kaiser_m = max(1, int(sum(value > 1 for value in eigenvalues)))
            scree_m = determine_scree_elbow(eigenvalues)
            parallel_m, thresholds = parallel_analysis(dataframe)
            self.root.after(
                0,
                lambda: self._show_factor_count(
                    eigenvalues, kaiser_m, scree_m, parallel_m, thresholds
                ),
            )
        except Exception as exc:
            error = str(exc)
            self.root.after(0, lambda: messagebox.showerror("Lỗi", error))
        finally:
            self.root.after(
                0, lambda: self.factor_count_button.config(state=tk.NORMAL)
            )

    def _show_factor_count(
        self, eigenvalues, kaiser_m, scree_m, parallel_m, thresholds
    ):
        output = (
            "1. QUY TẮC KAISER\n"
            f"Đề xuất: m = {kaiser_m}.\n"
            "Lý do: giữ các nhân tố có trị riêng > 1, nghĩa là mỗi nhân tố "
            "giải thích nhiều phương sai hơn một biến đã chuẩn hóa.\n"
            "Mức ý nghĩa: không áp dụng; đây là quy tắc quyết định, không phải "
            "kiểm định giả thuyết.\n\n"
            "2. SCREE PLOT\n"
            f"Đề xuất: m = {scree_m}.\n"
            "Lý do: điểm khuỷu được ước lượng bằng khoảng cách lớn nhất tới "
            "đường nối hai đầu dãy trị riêng; sau đó là phần đuôi tương đối phẳng.\n"
            "Mức ý nghĩa: không áp dụng; Scree Plot là phương pháp hình học/"
            "khám phá. Hãy đối chiếu điểm đánh dấu trên đồ thị.\n\n"
            "3. PARALLEL ANALYSIS (HORN)\n"
            f"Đề xuất: m = {parallel_m}.\n"
            "Lý do: giữ các trị riêng quan sát lớn hơn phân vị 95% của trị "
            "riêng từ 200 bộ dữ liệu ngẫu nhiên có cùng kích thước.\n"
            "Mức ý nghĩa: α = 0,05; chỉ khoảng 5% trị riêng ngẫu nhiên vượt "
            "ngưỡng. Đây là khuyến nghị chính vì có chuẩn đối chứng ngẫu nhiên."
        )
        self.factor_count_text.delete("1.0", tk.END)
        self.factor_count_text.insert(tk.END, output)
        self._draw_scree(eigenvalues, scree_m, thresholds)

    def _draw_scree(self, eigenvalues, selected_m=None, thresholds=None):
        self.scree_axis.clear()
        if len(eigenvalues):
            factors = list(range(1, len(eigenvalues) + 1))
            self.scree_axis.plot(
                factors, eigenvalues, marker="o", label="Trị riêng quan sát"
            )
            self.scree_axis.axhline(
                1, color="gray", linestyle="--", label="Kaiser = 1"
            )
            if thresholds is not None:
                self.scree_axis.plot(
                    factors, thresholds, linestyle="--", label="Ngưỡng PA 95%"
                )
            if selected_m:
                self.scree_axis.axvline(
                    selected_m,
                    color="red",
                    linestyle=":",
                    label=f"Điểm khuỷu m={selected_m}",
                )
            self.scree_axis.set_xticks(factors)
            self.scree_axis.legend(fontsize=8)
        self.scree_axis.set_title("Biểu đồ Scree Plot")
        self.scree_axis.set_xlabel("Số thứ tự nhân tố")
        self.scree_axis.set_ylabel("Trị riêng")
        self.scree_axis.grid(alpha=0.25)
        self.scree_figure.tight_layout()
        self.scree_canvas.draw()

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
