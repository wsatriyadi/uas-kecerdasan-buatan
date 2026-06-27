import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time

class BackpropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wisnu Satriyadi | UAS ANN")
        self.root.geometry("910x900")
        self.root.minsize(800, 700)
        
        self.bg_main      = "#ffffff"   # putih bersih
        self.bg_panel     = "#f2f2f2"   # abu-abu sangat muda (ribbon bg)
        self.bg_card      = "#ffffff"   # putih
        self.bg_header    = "#2b579a"   # biru Microsoft
        self.bg_accent    = "#0078d4"   # biru aksen Word
        self.bg_light     = "#e8f0fe"   # biru muda highlight
        self.bg_success   = "#d4edda"   # hijau muda sukses
        self.bg_warning   = "#fff3cd"   # kuning warning
        self.bg_danger    = "#f8d7da"   # merah muda error
        
        self.fg_primary   = "#1e1e1e"
        self.fg_secondary = "#4a4a4a"
        self.fg_dim       = "#7a7a7a"
        self.fg_white     = "#ffffff"
        self.fg_accent    = "#0078d4"
        self.fg_success   = "#155724"
        self.fg_error     = "#721c24"
        
        self.border_color = "#d0d0d0"
        self.separator    = "#e0e0e0"
        
        self.configure_root()
        
        # Stop event flag
        self.stop_event = threading.Event()
        self.calculation_running = False

        # Variables
        self.nim_var = tk.StringVar(value="310125023893")
        self.lr_var = tk.DoubleVar(value=1.0)
        self.max_epoch_var = tk.IntVar(value=3)
        self.target_error_var = tk.DoubleVar(value=0.01)
        self.e_var = tk.DoubleVar(value=2.71828183)

        self.d1_x1_var = tk.DoubleVar(value=0.9)
        self.d1_x2_var = tk.DoubleVar(value=0.4)
        self.d1_t_var = tk.IntVar(value=1)
        self.d2_x1_var = tk.DoubleVar(value=0.73)
        self.d2_x2_var = tk.DoubleVar(value=0.85)
        self.d2_t_var = tk.IntVar(value=0)

        self.setup_ui()

    def configure_root(self):
        self.root.configure(bg=self.bg_main)

    # ───────────────────────── helper widgets ─────────────────────────
    def _make_entry(self, parent, **kw):
        e = tk.Entry(parent, relief="solid", bd=1, highlightthickness=0,
                     font=("Segoe UI", 10), bg="white", fg=self.fg_primary,
                     selectbackground=self.bg_accent, selectforeground="white",
                     **kw)
        return e

    def _make_label(self, parent, text="", **kw):
        return tk.Label(parent, text=text, bg=self.bg_main, fg=self.fg_primary,
                        font=("Segoe UI", 10), anchor="w", **kw)

    def _make_framelabel(self, parent, text="", **kw):
        return tk.Label(parent, text=text, bg=self.bg_panel, fg=self.fg_accent,
                        font=("Segoe UI", 10, "bold"), anchor="w", **kw)

    def _make_button(self, parent, text="", **kw):
        bg = kw.pop("bg", self.bg_accent)
        fg = kw.pop("fg", "white")
        return tk.Button(parent, text=text, bg=bg, fg=fg,
                         font=("Segoe UI", 10, "bold"),
                         relief="flat", bd=0, padx=18, pady=6,
                         activebackground=self._darken(bg),
                         activeforeground=fg, cursor="hand2", **kw)

    @staticmethod
    def _darken(hex_color, amount=0.15):
        """Darken a hex color by amount (0-1)."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        r = int(r * (1 - amount))
        g = int(g * (1 - amount))
        b = int(b * (1 - amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ─────────────────────────── UI Layout ────────────────────────────
    def setup_ui(self):
        # ── TOP RIBBON ──
        ribbon = tk.Frame(self.root, bg=self.bg_header, height=48)
        ribbon.pack(fill=tk.X)
        ribbon.pack_propagate(False)

        tk.Label(ribbon, text="📘 KALKULATOR BACKPROPAGATION", fg="white",
                 bg=self.bg_header, font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=16, pady=10)
        tk.Label(ribbon, text="UAS ANN · Prediksi Kebangkrutan", fg="#b8d4f0",
                 bg=self.bg_header, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(4,16), pady=10)

        # ── MAIN CONTAINER (scrollable area) ──
        canvas = tk.Canvas(self.root, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg_main)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main = scroll_frame

        # ── 1. PARAMETER SECTION ──
        param_section = tk.Frame(main, bg=self.bg_main, highlightbackground=self.separator,
                                 highlightthickness=1, padx=16, pady=12)
        param_section.pack(fill=tk.X, padx=12, pady=(12,6))

        tk.Label(param_section, text="⚙️ Parameter Jaringan", font=("Segoe UI", 12, "bold"),
                 fg=self.fg_accent, bg=self.bg_main).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0,8))

        # Row 1
        tk.Label(param_section, text="NIM (12 digit):", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=(0,4), pady=4)
        e_nim = self._make_entry(param_section, textvariable=self.nim_var, width=14)
        e_nim.grid(row=1, column=1, sticky="w", padx=(0,16), pady=4)

        tk.Label(param_section, text="Multiplier:", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", padx=(0,4), pady=4)
        self.multiplier_label = tk.Label(param_section, text="0.3893", bg=self.bg_main,
                                          fg=self.fg_accent, font=("Segoe UI", 10, "bold"))
        self.multiplier_label.grid(row=1, column=3, sticky="w", padx=(0,16), pady=4)

        tk.Label(param_section, text="Konstanta e:", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=1, column=4, sticky="w", padx=(0,4), pady=4)
        self._make_entry(param_section, textvariable=self.e_var, width=12).grid(row=1, column=5, sticky="w", pady=4)

        # Row 2
        tk.Label(param_section, text="Learning Rate (α):", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=(0,4), pady=4)
        self._make_entry(param_section, textvariable=self.lr_var, width=8).grid(row=2, column=1, sticky="w", padx=(0,16), pady=4)

        tk.Label(param_section, text="Max Epoch:", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=2, column=2, sticky="w", padx=(0,4), pady=4)
        self._make_entry(param_section, textvariable=self.max_epoch_var, width=8).grid(row=2, column=3, sticky="w", padx=(0,16), pady=4)

        tk.Label(param_section, text="Target Error:", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=2, column=4, sticky="w", padx=(0,4), pady=4)
        self._make_entry(param_section, textvariable=self.target_error_var, width=12).grid(row=2, column=5, sticky="w", pady=4)

        # Update multiplier live
        def update_multiplier(*_):
            try:
                n = self.nim_var.get()
                if len(n) >= 4:
                    m = float(f"0.{n[-4:]}")
                    self.multiplier_label.config(text=f"{m:.4f}")
                else:
                    self.multiplier_label.config(text="NIM < 4 digit")
            except Exception:
                self.multiplier_label.config(text="Error")
        self.nim_var.trace_add("write", update_multiplier)

        # ── 2. DATA TRAINING SECTION ──
        data_section = tk.Frame(main, bg=self.bg_main, highlightbackground=self.separator,
                                highlightthickness=1, padx=16, pady=12)
        data_section.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(data_section, text="📊 Data Training (Sebelum Skalasi)", font=("Segoe UI", 12, "bold"),
                 fg=self.fg_accent, bg=self.bg_main).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0,8))

        # Headers
        headers = ["", "x₁ (Pendapatan)", "", "x₂ (Hutang)", "", "t (Target)"]
        for ci, h in enumerate(headers):
            if h:
                tk.Label(data_section, text=h, bg=self.bg_light, fg=self.fg_accent,
                         font=("Segoe UI", 9, "bold"), padx=6, pady=2,
                         relief="solid", bd=0).grid(row=1, column=ci, padx=2, pady=2, sticky="ew")
            else:
                tk.Label(data_section, text="", width=1, bg=self.bg_main).grid(row=1, column=ci)

        # Data 1
        tk.Label(data_section, text="📍 Data 1 (A) :", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=(0,4), pady=4)
        self._make_entry(data_section, textvariable=self.d1_x1_var, width=10).grid(row=2, column=1, padx=2, pady=4)
        tk.Label(data_section, text="|", bg=self.bg_main, fg=self.separator).grid(row=2, column=2)
        self._make_entry(data_section, textvariable=self.d1_x2_var, width=10).grid(row=2, column=3, padx=2, pady=4)
        tk.Label(data_section, text="|", bg=self.bg_main, fg=self.separator).grid(row=2, column=4)
        self._make_entry(data_section, textvariable=self.d1_t_var, width=6).grid(row=2, column=5, padx=2, pady=4)

        # Data 2
        tk.Label(data_section, text="📍 Data 2 (B) :", bg=self.bg_main, fg=self.fg_primary,
                 font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", padx=(0,4), pady=4)
        self._make_entry(data_section, textvariable=self.d2_x1_var, width=10).grid(row=3, column=1, padx=2, pady=4)
        tk.Label(data_section, text="|", bg=self.bg_main, fg=self.separator).grid(row=3, column=2)
        self._make_entry(data_section, textvariable=self.d2_x2_var, width=10).grid(row=3, column=3, padx=2, pady=4)
        tk.Label(data_section, text="|", bg=self.bg_main, fg=self.separator).grid(row=3, column=4)
        self._make_entry(data_section, textvariable=self.d2_t_var, width=6).grid(row=3, column=5, padx=2, pady=4)

        for ci in (1, 3, 5):
            data_section.columnconfigure(ci, weight=1)

        # ── 3. RULE BAR ──
        rule_frame = tk.Frame(main, bg=self.bg_light, highlightbackground=self.bg_accent,
                              highlightthickness=1, padx=12, pady=8)
        rule_frame.pack(fill=tk.X, padx=12, pady=6)

        nim_tail = self.nim_var.get()[-4:] if len(self.nim_var.get()) >= 4 else "XXXX"
        rule_text = f"📌 ATURAN: 4 digit terakhir NIM ({nim_tail}) = 0.{nim_tail} → pengali (multiplier) untuk semua data input (x1, x2) dan semua bobot awal. Target (t) TETAP / tidak dikalikan."
        self.rule_label = tk.Label(rule_frame, text=rule_text, bg=self.bg_light, fg=self.fg_secondary,
                                   font=("Segoe UI", 9, "italic"), anchor="w", justify="left")
        self.rule_label.pack(fill=tk.X)

        def update_rule(*_):
            try:
                n = self.nim_var.get()
                tail = n[-4:] if len(n) >= 4 else "XXXX"
                self.rule_label.config(text=f"📌 ATURAN: 4 digit terakhir NIM ({tail}) = 0.{tail} → pengali (multiplier) untuk semua data input (x1, x2) dan semua bobot awal. Target (t) TETAP / tidak dikalikan.")
                if len(n) >= 4:
                    m = float(f"0.{n[-4:]}")
                    self.multiplier_label.config(text=f"{m:.4f}")
                else:
                    self.multiplier_label.config(text="NIM < 4 digit")
            except Exception:
                pass
        self.nim_var.trace_add("write", update_rule)

        # ── 4. BUTTON BAR ──
        btn_bar = tk.Frame(main, bg=self.bg_main)
        btn_bar.pack(fill=tk.X, padx=12, pady=8)

        self.calc_btn = self._make_button(btn_bar, text="▶  HITUNG DETAIL", bg=self.bg_accent,
                                           command=self.start_calculation)
        self.calc_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = self._make_button(btn_bar, text="⏹  BERHENTI", bg="#c0392b",
                                           command=self.stop_calculation, state="disabled")
        self.stop_btn.pack(side=tk.LEFT)

        # Progress + Status
        status_frame = tk.Frame(btn_bar, bg=self.bg_main)
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(12, 0))

        self.progress = ttk.Progressbar(status_frame, mode="determinate", length=200)
        self.progress.pack(fill=tk.X, pady=(0, 3))

        self.status_label = tk.Label(status_frame, text="💡  Siap menjalankan perhitungan",
                                      bg=self.bg_main, fg=self.fg_dim,
                                      font=("Segoe UI", 9))
        self.status_label.pack(anchor="e")

        # ── 5. BOBOT INFO (collapsible hint) ──
        hint_frame = tk.Frame(main, bg=self.bg_light, highlightbackground=self.separator,
                              highlightthickness=1, padx=12, pady=6)
        hint_frame.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(hint_frame, text="📦 Bobot awal sudah di-hardcode sesuai soal UAS (PDF). Setelah tombol HITUNG diklik, bobot akan dikalikan multiplier NIM.",
                 bg=self.bg_light, fg=self.fg_secondary, font=("Segoe UI", 9)).pack(anchor="w")

        # ── 6. LOG PANEL ──
        log_section = tk.Frame(main, bg=self.bg_main, padx=0, pady=0)
        log_section.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

        # Log header
        log_header = tk.Frame(log_section, bg=self.bg_panel, highlightbackground=self.separator,
                               highlightthickness=1)
        log_header.pack(fill=tk.X)
        tk.Label(log_header, text="📝 LOG PERHITUNGAN DETAIL", bg=self.bg_panel, fg=self.fg_accent,
                 font=("Segoe UI", 10, "bold"), padx=10, pady=4).pack(side=tk.LEFT)

        # Log body
        log_body_frame = tk.Frame(log_section, highlightbackground=self.separator, highlightthickness=1)
        log_body_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_body_frame, wrap=tk.WORD, height=16, font=("Consolas", 9),
                                 bg="white", fg=self.fg_primary, insertbackground=self.fg_primary,
                                 relief="flat", bd=8, padx=8, pady=6)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        log_scroll = tk.Scrollbar(log_body_frame, command=self.log_text.yview)
        log_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.log_text.config(yscrollcommand=log_scroll.set)

        # Text tags
        tag_cfg = {
            "header":  ("Consolas", "10", "bold"),
            "epoch":   ("Consolas", "10", "bold"),
            "step":    ("Consolas", "9", "bold"),
            "info":    ("Consolas", "9", "normal"),
            "success": ("Consolas", "9", "normal"),
            "dim":     ("Consolas", "9", "normal"),
            "warn":    ("Consolas", "9", "bold"),
            "error":   ("Consolas", "9", "bold"),
        }
        for tag, (fam, sz, wgt) in tag_cfg.items():
            self.log_text.tag_config(tag, font=(fam, sz, wgt))

        self.log_text.tag_config("header", foreground=self.bg_header)
        self.log_text.tag_config("epoch", foreground=self.bg_accent)
        self.log_text.tag_config("step", foreground=self.bg_accent)
        self.log_text.tag_config("info", foreground=self.fg_primary)
        self.log_text.tag_config("success", foreground=self.fg_success)
        self.log_text.tag_config("dim", foreground=self.fg_dim)
        self.log_text.tag_config("warn", foreground="#856404")
        self.log_text.tag_config("error", foreground=self.fg_error)

        self.log_text.tag_config("bgstep", background=self.bg_light, foreground=self.fg_accent,
                                  font=("Consolas", "9", "bold"))

        # Welcome message
        self._welcome()

    def _welcome(self):
        self.log_text.insert("end", "━"*78 + "\n", "dim")
        self.log_text.insert("end", "  📘 KALKULATOR BACKPROPAGATION\n", "header")
        self.log_text.insert("end", "  Wisnu Satriyadi\n", "header")
        self.log_text.insert("end", "  UAS ANN · Prediksi Kebangkrutan Perusahaan\n", "header")
        self.log_text.insert("end", "━"*78 + "\n\n", "dim")
        self.log_text.insert("end", "  ▶ Atur parameter di atas, lalu klik tombol HITUNG DETAIL\n", "info")
        self.log_text.insert("end", f"  ▶ Contoh NIM: 310125023893 → multiplier = 0.3893\n", "info")
        self.log_text.insert("end", "  ▶ Bobot awal: hardcode sesuai PDF soal UAS\n\n", "info")

    # ────────────────────── Logging helpers ──────────────────────
    def log(self, msg, tag="info"):
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.root.update_idletasks()

    def log_h(self, msg):  self.log(msg, "header")
    def log_e(self, msg):  self.log(msg, "epoch")
    def log_s(self, msg):  self.log(msg, "step")
    def log_ok(self, msg): self.log(msg, "success")
    def log_dim(self, msg): self.log(msg, "dim")
    def log_warn(self, msg): self.log(msg, "warn")
    def log_err(self, msg): self.log(msg, "error")
    def log_bg(self, msg): self.log(msg, "bgstep")

    # ────────────────────── Button handlers ──────────────────────
    def start_calculation(self):
        if self.calculation_running:
            return
        self.calculation_running = True
        self.stop_event.clear()

        self.calc_btn.config(state="disabled", text="⚙  Menghitung...", bg="#999")
        self.stop_btn.config(state="normal", bg="#c0392b")
        self.status_label.config(text="⏳  Sedang menghitung...", fg=self.fg_accent)
        self.progress["value"] = 0

        self.log_text.delete("1.0", "end")

        t = threading.Thread(target=self._run_calc, daemon=True)
        t.start()

    def stop_calculation(self):
        self.stop_event.set()
        self.status_label.config(text="⏹  Menghentikan perhitungan...", fg=self.fg_error)

    # ────────────────────── Core calculation ─────────────────────
    def _run_calc(self):
        try:
            nim_str = self.nim_var.get()
            if len(nim_str) < 4:
                self.log_err("✖ ERROR: NIM harus minimal 4 digit.")
                return

            multiplier = float(f"0.{nim_str[-4:]}")
            alpha       = self.lr_var.get()
            max_epoch   = self.max_epoch_var.get()
            target_err  = self.target_error_var.get()
            e           = self.e_var.get()

            self.log("━"*78, "dim")
            self.log_h("  MULAI PERHITUNGAN BACKPROPAGATION")
            self.log("━"*78, "dim")
            self.log(f"  NIM           : {nim_str}  →  4 digit: {nim_str[-4:]}")
            self.log(f"  Multiplier    : {multiplier:.4f}", "success")
            self.log(f"  Learning Rate : {alpha}")
            self.log(f"  Max Epoch     : {max_epoch}")
            self.log(f"  Target Error  : {target_err}")
            self.log(f"  Konstanta e   : {e}")
            self.log("─"*78, "dim")

            # ── Hardcoded initial weights (before scaling) ──
            v_init = {"v11":0.9562,"v12":0.7762,"v13":0.1623,"v14":0.2886,
                      "v21":0.1962,"v22":0.6133,"v23":0.0311,"v24":0.9711,
                      "V01":0.7496,"V02":0.3796,"V03":0.7256,"V04":0.1628}
            w_init = {"w1":0.2280,"w2":0.9585,"w3":0.6799,"w4":0.0550,"w0":0.9505}

            v = {k: val*multiplier for k,val in v_init.items()}
            w = {k: val*multiplier for k,val in w_init.items()}

            d1_x1 = self.d1_x1_var.get() * multiplier
            d1_x2 = self.d1_x2_var.get() * multiplier
            d1_t  = self.d1_t_var.get()
            d2_x1 = self.d2_x1_var.get() * multiplier
            d2_x2 = self.d2_x2_var.get() * multiplier
            d2_t  = self.d2_t_var.get()

            dataset = [
                {"x1":d1_x1,"x2":d1_x2,"t":d1_t,"label":"Data 1 (Perusahaan A)"},
                {"x1":d2_x1,"x2":d2_x2,"t":d2_t,"label":"Data 2 (Perusahaan B)"},
            ]

            self.log("", "step")
            self.log_bg("  DATA TRAINING (setelah × multiplier):")
            self.log(f"    Data 1: x₁={d1_x1:.6f}  x₂={d1_x2:.6f}  t={d1_t}")
            self.log(f"    Data 2: x₁={d2_x1:.6f}  x₂={d2_x2:.6f}  t={d2_t}")
            self.log("", "step")
            self.log_bg("  BOBOT AWAL (setelah × multiplier):")
            self.log(f"    v = { {k:round(v,6) for k,v in v.items()} }")
            self.log(f"    w = { {k:round(v,6) for k,v in w.items()} }")
            self.log("─"*78, "dim")

            # ── Main epoch loop ──
            for epoch in range(1, max_epoch+1):
                if self.stop_event.is_set():
                    self.log_warn("\n  ⏹ Perhitungan DIHENTIKAN oleh pengguna.")
                    break

                self.log("", "epoch")
                self.log("┌"+"─"*60+"┐", "dim")
                self.log_e(f"│          EPOCH {epoch} dari {max_epoch}")
                self.log("└"+"─"*60+"┘", "dim")

                self.progress["value"] = ((epoch-1)/max_epoch)*100
                self.root.update_idletasks()
                total_mse = 0.0

                for i, data in enumerate(dataset):
                    if self.stop_event.is_set():
                        break

                    self.log("", "step")
                    self.log_bg(f"  ═══ {data['label']} ═══")

                    # ── FORWARD ──
                    self.log_s("\n  📤 FORWARD PASS")
                    self.log_s("  [1] Hidden Layer (z₁–z₄):")
                    z_in, z_out = {}, {}
                    for j in range(1,5):
                        v0j, v1j, v2j = v[f"V0{j}"], v[f"v1{j}"], v[f"v2{j}"]
                        x1v = data["x1"]*v1j
                        x2v = data["x2"]*v2j
                        z_in[j] = v0j + x1v + x2v
                        z_out[j] = 1/(1 + e**(-z_in[j]))
                        self.log(f"      z_in{j} = {v0j:.6f} + ({data['x1']:.6f}×{v1j:.6f}) + ({data['x2']:.6f}×{v2j:.6f})")
                        self.log(f"              = {v0j:.6f} + {x1v:.6f} + {x2v:.6f} = {z_in[j]:.6f}")
                        self.log(f"      z_{j}    = sigmoid({z_in[j]:.6f}) = {z_out[j]:.6f}")

                    self.log_s("\n  [2] Output Layer (y):")
                    parts = [f"{z_out[j]:.6f}×{w[f'w{j}']:.6f}" for j in range(1,5)]
                    self.log(f"      y_in = {w['w0']:.6f} + {' + '.join(parts)}")
                    y_in = w["w0"] + sum(z_out[j]*w[f"w{j}"] for j in range(1,5))
                    y    = 1/(1 + e**(-y_in))
                    self.log(f"           = {y_in:.6f}")
                    self.log(f"      y    = sigmoid({y_in:.6f}) = {y:.6f}")

                    error = data["t"] - y
                    total_mse += error**2

                    self.log_s("\n  [3] Error & MSE:")
                    self.log(f"      Error = {data['t']} − {y:.6f} = {error:.6f}")
                    self.log(f"      MSE   = ({error:.6f})² = {error**2:.6f}")

                    # ── BACKWARD ──
                    self.log_s("\n  📥 BACKWARD PASS")
                    self.log_s("  [1] Delta Output Layer:")
                    y1y = y*(1-y)
                    delta_out = error * y * (1-y)
                    self.log(f"      y×(1−y)  = {y:.6f}×{1-y:.6f} = {y1y:.6f}")
                    self.log(f"      δ_output = error×y×(1−y) = {error:.6f}×{y1y:.6f} = {delta_out:.6f}")

                    self.log_s("\n  [2] Update Bobot Hidden → Output (w):")
                    w_old = w.copy()
                    dw0 = alpha*delta_out
                    w["w0"] += dw0
                    self.log(f"      Δw₀ = {alpha}×{delta_out:.6f} = {dw0:.6f}  →  w₀: {w_old['w0']:.6f} → {w['w0']:.6f}")
                    for j in range(1,5):
                        dwj = alpha*delta_out*z_out[j]
                        w[f"w{j}"] += dwj
                        self.log(f"      Δw{j} = {alpha}×{delta_out:.6f}×{z_out[j]:.6f} = {dwj:.6f}  →  w{j}: {w_old[f'w{j}']:.6f} → {w[f'w{j}']:.6f}")

                    self.log_s("\n  [3] Propagasi Error ke Hidden Layer:")
                    delta_h = {}
                    for j in range(1,5):
                        din = delta_out * w_old[f"w{j}"]
                        delta_h[j] = din * z_out[j]*(1-z_out[j])
                        self.log(f"      δ_in{j} = {delta_out:.6f}×{w_old[f'w{j}']:.6f} = {din:.6f}")
                        self.log(f"      δ_h{j}  = {din:.6f}×{z_out[j]:.6f}×{1-z_out[j]:.6f} = {delta_h[j]:.6f}")

                    self.log_s("\n  [4] Update Bobot Input → Hidden (v):")
                    v_old = v.copy()
                    for j in range(1,5):
                        dv1 = alpha*delta_h[j]*data["x1"]
                        dv2 = alpha*delta_h[j]*data["x2"]
                        dV0 = alpha*delta_h[j]
                        v[f"v1{j}"] += dv1
                        v[f"v2{j}"] += dv2
                        v[f"V0{j}"] += dV0
                        self.log(f"      z{j}: Δv1{j}={dv1:.6f}  Δv2{j}={dv2:.6f}  ΔV0{j}={dV0:.6f}")
                        self.log(f"           v1{j}: {v_old[f'v1{j}']:.6f} → {v[f'v1{j}']:.6f}")
                        self.log(f"           v2{j}: {v_old[f'v2{j}']:.6f} → {v[f'v2{j}']:.6f}")
                        self.log(f"           V0{j}: {v_old[f'V0{j}']:.6f} → {v[f'V0{j}']:.6f}")

                if self.stop_event.is_set():
                    break

                epoch_mse = total_mse / len(dataset)
                self.log("", "dim")
                self.log("  "+"─"*50, "dim")
                self.log_ok(f"  ✅ HASIL EPOCH {epoch}: MSE = {epoch_mse:.6f}")
                self.log("  "+"─"*50, "dim")

                self.progress["value"] = (epoch/max_epoch)*100
                self.root.update_idletasks()

                # Check target error convergence
                if epoch_mse <= target_err:
                    self.log("", "success")
                    self.log_ok(f"🎯 TARGET ERROR TERCAPAI! MSE ({epoch_mse:.6f}) ≤ Target ({target_err})")
                    self.log_ok(f"✅ Konvergensi pada Epoch {epoch}")
                    break

                time.sleep(0.08)

            # ── Final summary ──
            if not self.stop_event.is_set():
                self.log("", "dim")
                self.log("━"*78, "dim")
                self.log_h("  ✅ PERHITUNGAN SELESAI")
                self.log("━"*78, "dim")
                self.log_ok(f"\n  Bobot Akhir Setelah {max_epoch} Epoch:")
                self.log(f"    v = { {k:round(v,6) for k,v in v.items()} }")
                self.log(f"    w = { {k:round(v,6) for k,v in w.items()} }")
                self.log(f"\n    Multiplier: {multiplier}  (NIM: {nim_str})")
                self.log("━"*78, "dim")
                self.status_label.config(text="✅  Perhitungan selesai", fg=self.fg_success)
                self.progress["value"] = 100

        except Exception as ex:
            self.log_err(f"\n  ❌ ERROR: {ex}")
            import traceback
            self.log(traceback.format_exc(), "dim")
        finally:
            self.calculation_running = False
            self.calc_btn.config(state="normal", text="▶  HITUNG DETAIL", bg=self.bg_accent)
            self.stop_btn.config(state="disabled", bg="#999")
            self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = BackpropApp(root)
    root.mainloop()
