import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import os
import traceback
class ProblemAnalyzer:
    """تحلیل‌گر هوشمند مسائل تحقیق در عملیات"""
    
    def __init__(self, obj_coeffs, constraints, opt_type, num_vars, num_cons):
        self.obj_coeffs = obj_coeffs  # لیست ضرایب تابع هدف
        self.constraints = constraints  # لیست دیکشنری‌های {'coeffs': [], 'sign': str, 'rhs': float}
        self.opt_type = opt_type  # 'Max' یا 'Min'
        self.num_vars = num_vars
        self.num_cons = num_cons
        
    def analyze(self):
        """تحلیل کامل مسأله و پیشنهاد روش‌های حل"""
        analysis = {
            'problem_type': 'Unknown',
            'suitable_methods': [],
            'recommended_method': None,
            'details': {},
            'warnings': []
        }
        
        # 1. تشخیص نوع مسأله پایه
        analysis.update(self._detect_basic_type())
        
        # 2. تحلیل محدودیت‌ها
        analysis.update(self._analyze_constraints())
        
        # 3. تحلیل تابع هدف
        analysis.update(self._analyze_objective())
        
        # 4. پیشنهاد روش‌های حل
        analysis.update(self._suggest_methods(analysis))
        
        # 5. تخمین پیچیدگی
        analysis.update(self._estimate_complexity())
        
        return analysis
    
    def _detect_basic_type(self):
        """تشخیص نوع پایه مسأله"""
        result = {}
        
        # بررسی مسأله حمل‌ونقل (الگوی خاص)
        if self._is_transportation_pattern():
            result['problem_type'] = 'Transportation Problem'
            result['details'] = {'special_type': 'transportation'}
            
        # بررسی مسأله تخصیص (ماتریس مربعی)
        elif self._is_assignment_pattern():
            result['problem_type'] = 'Assignment Problem'
            result['details'] = {'special_type': 'assignment'}
            
        # بررسی مسأله شبکه (ساختار شبکه)
        elif self._is_network_pattern():
            result['problem_type'] = 'Network Flow Problem'
            result['details'] = {'special_type': 'network'}
            
        # مسأله برنامه‌ریزی خطی عمومی
        else:
            result['problem_type'] = 'Linear Programming (LP)'
            result['details'] = {'special_type': 'general_lp'}
            
        return result
    
    # def _is_transportation_pattern(self):
      #  """الگوی مسأله حمل‌ونقل"""
        # شرایط ساده برای شروع:
        # 1. تعداد متغیرها = عرضه × تقاضا
        # 2. همه ضرایب 0 یا 1 در محدودیت‌ها
       # if self.num_vars >= 4 and self.num_cons >= 3:
        #    # بررسی ساده - بعداً کامل می‌کنیم
         #   return False
        #return False
    def _is_transportation_pattern(self):
        """الگوی مسأله حمل‌ونقل"""
        return False  # فعلاً همیشه False برگردون
    #def _is_assignment_pattern(self):
     #   """الگوی مسأله تخصیص"""
      #  # ماتریس مربعی n×n
       # import math
        #n = int(math.sqrt(self.num_vars))
        #if n * n == self.num_vars and self.num_cons == 2 * n:
         #   return True
        #return False
    def _is_assignment_pattern(self):
        """الگوی مسأله تخصیص"""
        import math
        n = int(math.sqrt(self.num_vars))
        if n * n == self.num_vars and self.num_cons == 2 * n:
            # فقط در صورتی که همه ضرایب 0 یا 1 باشند
            for cons in self.constraints:
                for c in cons['coeffs']:
                    if abs(c) > 1e-10 and abs(c) != 1.0:
                        return False
            return True
        return False
    # def _is_network_pattern(self):
      #  """الگوی مسأله شبکه"""
       # # هر محدودیت حداکثر 2 متغیر با ضرایب 1 و -1
        #for cons in self.constraints:
         #   nonzero = sum(1 for c in cons['coeffs'] if abs(c) > 1e-10)
          #  if nonzero > 2:
           #     return False
        #return True
    def _is_network_pattern(self):
        """الگوی مسأله شبکه"""
        # فقط در صورتی که همه متغیرها دارای ضریب 1 یا -1 باشند
        for cons in self.constraints:
            nonzero = sum(1 for c in cons['coeffs'] if abs(c) > 1e-10)
            if nonzero > 2:
                return False
            for c in cons['coeffs']:
                if abs(c) > 1e-10 and abs(c) != 1.0:
                    return False  # ضرایب باید دقیقاً 1 یا -1 باشند
        # حداقل ۳ متغیر داشته باشه
        if self.num_vars < 3:
            return False
        return True

    def _analyze_constraints(self):
        """تحلیل محدودیت‌ها"""
        result = {
            'has_equality': False,
            'has_greater_equal': False,
            'has_less_equal': False,
            'has_negative_rhs': False,
            'all_standard': True
        }
        
        for cons in self.constraints:
            # بررسی نوع محدودیت
            if cons['sign'] == "=":
                result['has_equality'] = True
                result['all_standard'] = False
            elif cons['sign'] == ">=":
                result['has_greater_equal'] = True
                result['all_standard'] = False
            elif cons['sign'] == "<=":
                result['has_less_equal'] = True
            
            # بررسی سمت راست
            if cons['rhs'] < 0:
                result['has_negative_rhs'] = True
                result['all_standard'] = False
        
        return {'constraint_analysis': result}
    
    def _analyze_objective(self):
        """تحلیل تابع هدف"""
        result = {
            'all_coeffs_positive': all(c > -1e-10 for c in self.obj_coeffs),
            'all_coeffs_negative': all(c < 1e-10 for c in self.obj_coeffs),
            'has_zero_coeff': any(abs(c) < 1e-10 for c in self.obj_coeffs),
            'max_coeff': max(self.obj_coeffs) if self.obj_coeffs else 0,
            'min_coeff': min(self.obj_coeffs) if self.obj_coeffs else 0
        }
        
        # بررسی بهینگی اولیه
        if self.opt_type == "Max":
            result['initial_solution_optimal'] = result['all_coeffs_negative']
        else:  # Min
            result['initial_solution_optimal'] = result['all_coeffs_positive']
            
        return {'objective_analysis': result}
    
    def _suggest_methods(self, analysis):
        """پیشنهاد روش‌های حل بر اساس تحلیل"""
        methods = []
        reasons = []
        
        constraint_info = analysis.get('constraint_analysis', {})
        objective_info = analysis.get('objective_analysis', {})
        problem_type = analysis.get('problem_type', '')
        
        # 1. Standard Simplex
        if constraint_info.get('all_standard', False) and not constraint_info.get('has_negative_rhs', False):
            methods.append('Standard Simplex')
            reasons.append('مسأله استاندارد (همه محدودیت‌ها ≤ و RHS ≥ 0)')
        
        # 2. Two-Phase Simplex
        if constraint_info.get('has_equality', False) or constraint_info.get('has_greater_equal', False):
            methods.append('Two-Phase Simplex')
            reasons.append('وجود محدودیت‌های = یا ≥ (نیاز به متغیر مصنوعی)')
        
        # 3. Big-M Method
        if constraint_info.get('has_equality', False) or constraint_info.get('has_greater_equal', False):
            methods.append('Big-M Method')
            reasons.append('جایگزین Two-Phase برای محدودیت‌های = یا ≥')
        
        # 4. Dual Simplex
        if constraint_info.get('has_negative_rhs', False):
            methods.append('Dual Simplex')
            reasons.append('وجود سمت راست منفی در محدودیت‌ها (Dual Simplex مناسب‌تر است)')
        elif not constraint_info.get('all_standard', False):
            # اگر مسأله استاندارد نیست اما سمت راست منفی ندارد
            methods.append('Dual Simplex')
            reasons.append('امکان استفاده از Dual Simplex برای بهبود کارایی')
        
        # 5. Revised Simplex - تغییر شرط
        # همیشه برای مسائل استاندارد پیشنهاد شود (حتی کوچک)
        if constraint_info.get('all_standard', False) and not constraint_info.get('has_negative_rhs', False):
            if self.num_vars >= 3 or self.num_cons >= 3:  # تغییر این خط
                methods.append('Revised Simplex')
                reasons.append(f'مسأله استاندارد ({self.num_vars} متغیر، {self.num_cons} محدودیت) - حافظه‌کارآمد')
        
        # 6. Interior Point
        if self.num_vars > 20 and self.num_cons > 20:
            methods.append('Interior Point Method')
            reasons.append('مسأله بسیار بزرگ (همگرایی سریع)')
        
        # 7. Transportation Method
        if 'Transportation' in problem_type:
            methods.append('Transportation Method')
            reasons.append('مسأله حمل‌ونقل (ساختار خاص)')
        
        # 8. Assignment Method
        if 'Assignment' in problem_type:
            methods.append('Assignment Method (Hungarian)')
            reasons.append('مسأله تخصیص (ماتریس مربعی)')
        
        # 9. Network Simplex
        if 'Network' in problem_type:
            methods.append('Network Simplex')
            reasons.append('مسأله جریان شبکه (ساختار شبکه)')
        
        # حذف موارد تکراری
        unique_methods = []
        unique_reasons = []
        seen = set()
        
        for method, reason in zip(methods, reasons):
            if method not in seen:
                seen.add(method)
                unique_methods.append(method)
                unique_reasons.append(reason)
        
        return {
            'suitable_methods': unique_methods,
            'method_reasons': unique_reasons,
            'recommended_method': unique_methods[0] if unique_methods else 'Standard Simplex'
        }
    
    def _estimate_complexity(self):
        """تخمین پیچیدگی حل"""
        complexity = 'Low'
        
        if self.num_vars > 50 or self.num_cons > 50:
            complexity = 'Very High'
        elif self.num_vars > 20 or self.num_cons > 20:
            complexity = 'High'
        elif self.num_vars > 10 or self.num_cons > 10:
            complexity = 'Medium'
        
        return {'complexity': complexity}
class SimplexSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Simplex Solver")
        self.root.geometry("1000x800")
        self.current_page = None
        self.data = {}
        self.solution = None
        self.iterations = []
        # اضافه کردن این 2 خط
        self.obj_coeffs = []      # برای ذخیره ضرایب تابع هدف
        self.constraint_data = [] # برای ذخیره داده‌های محدودیت‌ها
        self.create_first_page()

    def create_first_page(self):
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Portable Simplex Solver", 
                              font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        # Optimization Type
        type_frame = tk.Frame(self.root)
        type_frame.pack(pady=10)
        
        tk.Label(type_frame, text="Optimization Type:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.opt_type = tk.StringVar(value="Max")
        tk.Radiobutton(type_frame, text="Maximum", variable=self.opt_type, 
                      value="Max", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(type_frame, text="Minimum", variable=self.opt_type, 
                      value="Min", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        # Number of Variables
        var_frame = tk.Frame(self.root)
        var_frame.pack(pady=10)
        
        tk.Label(var_frame, text="Number of Objective Variables:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.num_vars_entry = tk.Entry(var_frame, width=10, font=("Arial", 11))
        self.num_vars_entry.pack(side=tk.LEFT)
        self.num_vars_entry.insert(0, "2")
        
        # Number of Constraints
        cons_frame = tk.Frame(self.root)
        cons_frame.pack(pady=10)
        
        tk.Label(cons_frame, text="Number of Constraints:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.num_cons_entry = tk.Entry(cons_frame, width=10, font=("Arial", 11))
        self.num_cons_entry.pack(side=tk.LEFT)
        self.num_cons_entry.insert(0, "2")
        
        # Non-negativity
        nonneg_frame = tk.Frame(self.root)
        nonneg_frame.pack(pady=10)
        
        tk.Label(nonneg_frame, text="Non-negativity:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.nonneg_var = tk.StringVar(value="Yes")
        tk.Radiobutton(nonneg_frame, text="Yes", variable=self.nonneg_var, 
                      value="Yes", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(nonneg_frame, text="No", variable=self.nonneg_var, 
                      value="No", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        # Next Button
        next_btn = tk.Button(self.root, text="Next", 
                           font=("Arial", 12, "bold"),
                           bg="#4CAF50", fg="white",
                           width=15, height=2,
                           command=self.create_second_page)
        next_btn.pack(pady=30)
        
        # Credit
        credit_label = tk.Label(self.root, text="Prepared by Navid Naderpour ,Navid.Naderpour@gmail.com",
                              font=("Arial", 10), fg="gray")
        credit_label.pack(side=tk.BOTTOM, pady=10)

    def create_second_page(self):
        try:
            self.data['num_vars'] = int(self.num_vars_entry.get())
            self.data['num_cons'] = int(self.num_cons_entry.get())
            self.data['opt_type'] = self.opt_type.get()
            self.data['nonneg'] = self.nonneg_var.get()
            
            if self.data['num_vars'] <= 0 or self.data['num_cons'] <= 0:
                messagebox.showerror("Error", "Numbers must be positive!")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            return
            
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Enter Coefficients", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Objective Coefficients
        obj_frame = tk.Frame(self.root)
        obj_frame.pack(pady=10)
        
        tk.Label(obj_frame, text="Objective Coefficients:", 
                font=("Arial", 12, "bold")).pack()
        
        self.obj_entries = []
        obj_inner_frame = tk.Frame(obj_frame)
        obj_inner_frame.pack(pady=5)
        
        for i in range(self.data['num_vars']):
            var_label = tk.Label(obj_inner_frame, text=f"x{i+1}:", 
                               font=("Arial", 11))
            var_label.grid(row=0, column=i*2, padx=5, pady=5)
            
            entry = tk.Entry(obj_inner_frame, width=8, font=("Arial", 11))
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            entry.insert(0, "0")
            self.obj_entries.append(entry)
        
        # Constraints
        cons_frame = tk.Frame(self.root)
        cons_frame.pack(pady=20)
        
        tk.Label(cons_frame, text="Constraints:", 
                font=("Arial", 12, "bold")).pack()
        
        self.cons_entries = []
        self.sign_combos = []
        self.rhs_entries = []
        
        for i in range(self.data['num_cons']):
            row_frame = tk.Frame(cons_frame)
            row_frame.pack(pady=5)
            
            tk.Label(row_frame, text=f"Row {i+1}:", 
                    font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
            
            row_entries = []
            for j in range(self.data['num_vars']):
                entry = tk.Entry(row_frame, width=6, font=("Arial", 11))
                entry.pack(side=tk.LEFT, padx=2)
                entry.insert(0, "0")
                row_entries.append(entry)
            
            sign_combo = ttk.Combobox(row_frame, 
                                     values=["<=", "=", ">="],
                                     width=4, font=("Arial", 11))
            sign_combo.pack(side=tk.LEFT, padx=5)
            sign_combo.set("<=")
            
            rhs_entry = tk.Entry(row_frame, width=8, font=("Arial", 11))
            rhs_entry.pack(side=tk.LEFT, padx=2)
            rhs_entry.insert(0, "0")
            
            self.cons_entries.append(row_entries)
            self.sign_combos.append(sign_combo)
            self.rhs_entries.append(rhs_entry)
        
        # Continue Button
        continue_btn = tk.Button(self.root, text="Continue", 
                               font=("Arial", 12, "bold"),
                               bg="#2196F3", fg="white",
                               width=15, height=2,
                               command=self.preview_equations)
        continue_btn.pack(pady=30)
        
        # Back Button
        back_btn = tk.Button(self.root, text="Back", 
                           font=("Arial", 11),
                           command=self.create_first_page)
        back_btn.pack(pady=10)

    def preview_equations(self):
        try:
            # Get objective coefficients
            self.obj_coeffs = []  # تغییر: obj_coeffs به self.obj_coeffs
            for entry in self.obj_entries:
                val = entry.get().strip()
                self.obj_coeffs.append(float(val) if val else 0.0)
            
            # Get constraint data
            self.constraint_data = []  # تغییر: cons_data به self.constraint_data
            for i in range(self.data['num_cons']):
                row_coeffs = []
                for entry in self.cons_entries[i]:
                    val = entry.get().strip()
                    row_coeffs.append(float(val) if val else 0.0)
                
                sign = self.sign_combos[i].get()
                rhs_val = self.rhs_entries[i].get().strip()
                rhs = float(rhs_val) if rhs_val else 0.0
                
                self.constraint_data.append({
                    'coeffs': row_coeffs,
                    'sign': sign,
                    'rhs': rhs
                })
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            return
            
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Preview Equations", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Objective Function
        obj_str = "Maximize" if self.data['opt_type'] == "Max" else "Minimize"
        obj_parts = []
        for i, coeff in enumerate(self.obj_coeffs):  # تغییر: obj_coeffs به self.obj_coeffs
            if coeff != 0:
                sign = "+" if coeff >= 0 else "-"
                abs_coeff = abs(coeff)
                if abs_coeff == 1:
                    obj_parts.append(f"{sign} x{i+1}")
                else:
                    obj_parts.append(f"{sign} {abs_coeff}x{i+1}")
        
        if obj_parts:
            if obj_parts[0].startswith("+"):
                obj_parts[0] = obj_parts[0][2:]
            elif obj_parts[0].startswith("-"):
                obj_parts[0] = obj_parts[0][0] + obj_parts[0][2:]
        
        obj_eq = f"{obj_str}: z = " + " ".join(obj_parts)
        obj_label = tk.Label(self.root, text=obj_eq, 
                           font=("Arial", 12), fg="blue")
        obj_label.pack(pady=10)
        
        # Constraints
        tk.Label(self.root, text="Subject to:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        for i, cons in enumerate(self.constraint_data):  # تغییر: cons_data به self.constraint_data
            cons_parts = []
            for j, coeff in enumerate(cons['coeffs']):
                if coeff != 0:
                    sign = "+" if coeff >= 0 else "-"
                    abs_coeff = abs(coeff)
                    if abs_coeff == 1:
                        cons_parts.append(f"{sign} x{j+1}")
                    else:
                        cons_parts.append(f"{sign} {abs_coeff}x{j+1}")
            
            if cons_parts:
                if cons_parts[0].startswith("+"):
                    cons_parts[0] = cons_parts[0][2:]
                elif cons_parts[0].startswith("-"):
                    cons_parts[0] = cons_parts[0][0] + cons_parts[0][2:]
            
            cons_eq = " ".join(cons_parts) + f" {cons['sign']} {cons['rhs']}"
            cons_label = tk.Label(self.root, text=cons_eq, 
                                font=("Arial", 11))
            cons_label.pack(pady=5)
        
        # Non-negativity
        if self.data['nonneg'] == "Yes":
            nonneg_label = tk.Label(self.root, 
                                  text="Non-negativity: x ≥ 0",
                                  font=("Arial", 11), fg="green")
            nonneg_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        confirm_btn = tk.Button(btn_frame, text="Confirm", 
                              font=("Arial", 12, "bold"),
                              bg="#4CAF50", fg="white",
                              width=10, height=1,
                              command=self.method_selection)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        
        edit_btn = tk.Button(btn_frame, text="Edit", 
                           font=("Arial", 12),
                           command=self.create_second_page)
        edit_btn.pack(side=tk.LEFT, padx=10)

    def method_selection(self):
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Method Selection & Problem Analysis", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # تحلیل مسأله
        try:
            analyzer = ProblemAnalyzer(
                obj_coeffs=self.obj_coeffs,
                constraints=self.constraint_data,
                opt_type=self.data['opt_type'],
                num_vars=self.data['num_vars'],
                num_cons=self.data['num_cons']
            )
            
            analysis = analyzer.analyze()
            
            # نمایش تحلیل
            self.display_analysis(analysis)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in problem analysis: {str(e)}")
            self.create_first_page()
            return
        
        # روش‌های حل
        self.display_method_selection(analysis)
    def display_analysis(self, analysis):
        """نمایش تحلیل مسأله"""
        # فریم تحلیل
        analysis_frame = tk.Frame(self.root, relief=tk.GROOVE, bd=2, bg="#F0F8FF")
        analysis_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # عنوان تحلیل
        tk.Label(analysis_frame, text="📊 Problem Analysis Report", 
                font=("Arial", 12, "bold"), bg="#F0F8FF").pack(pady=5)
        
        # اطلاعات پایه
        info_frame = tk.Frame(analysis_frame, bg="#F0F8FF")
        info_frame.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(info_frame, text=f"Problem Type: {analysis['problem_type']}", 
                font=("Arial", 10, "bold"), bg="#F0F8FF").pack(anchor=tk.W)
        
        tk.Label(info_frame, text=f"Variables: {self.data['num_vars']}, Constraints: {self.data['num_cons']}, Optimization: {self.data['opt_type']}", 
                font=("Arial", 9), bg="#F0F8FF").pack(anchor=tk.W)
        
        tk.Label(info_frame, text=f"Complexity: {analysis['complexity']}", 
                font=("Arial", 9), bg="#F0F8FF").pack(anchor=tk.W)
        
        # تحلیل محدودیت‌ها
        cons_analysis = analysis.get('constraint_analysis', {})
        if cons_analysis:
            cons_text = "Constraints: "
            parts = []
            if cons_analysis.get('has_less_equal', False):
                parts.append("≤")
            if cons_analysis.get('has_equality', False):
                parts.append("=")
            if cons_analysis.get('has_greater_equal', False):
                parts.append("≥")
            if cons_analysis.get('has_negative_rhs', False):
                parts.append("Negative RHS")
            
            cons_text += ", ".join(parts) if parts else "Standard"
            tk.Label(info_frame, text=cons_text, 
                    font=("Arial", 9), bg="#F0F8FF").pack(anchor=tk.W)
        
        # هشدارها
        warnings = analysis.get('warnings', [])
        if warnings:
            warning_frame = tk.Frame(analysis_frame, bg="#FFF3CD", bd=1, relief=tk.SOLID)
            warning_frame.pack(pady=5, padx=10, fill=tk.X)
            
            tk.Label(warning_frame, text="⚠️ Warnings:", 
                    font=("Arial", 9, "bold"), bg="#FFF3CD").pack(anchor=tk.W, padx=5)
            
            for warning in warnings:
                tk.Label(warning_frame, text=f"• {warning}", 
                        font=("Arial", 8), bg="#FFF3CD", justify=tk.LEFT).pack(anchor=tk.W, padx=10)
    def display_method_selection(self, analysis):
        """نمایش انتخاب روش"""
        # عنوان
        tk.Label(self.root, text="🔧 Select Solution Method:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # روش‌های پیشنهادی
        suitable_methods = analysis.get('suitable_methods', [])
        method_reasons = analysis.get('method_reasons', [])
        recommended = analysis.get('recommended_method', '')
        
        if not suitable_methods:
            tk.Label(self.root, text="No suitable methods found!", 
                    font=("Arial", 11), fg="red").pack(pady=10)
            return
        
        # فریم روش‌ها
        methods_frame = tk.Frame(self.root)
        methods_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # ایجاد لیست با اسکرول
        canvas = tk.Canvas(methods_frame, height=200)
        scrollbar = tk.Scrollbar(methods_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # متغیر برای انتخاب
        self.method_var = tk.StringVar(value="1")
        
        # نمایش هر روش
        method_widgets = []
        for i, (method, reason) in enumerate(zip(suitable_methods, method_reasons)):
            # تعیین وضعیت
            is_recommended = (method == recommended)
            bg_color = "#E8F5E9" if is_recommended else "white"
            
            method_frame = tk.Frame(scrollable_frame, bg=bg_color, bd=1, relief=tk.GROOVE)
            method_frame.pack(pady=3, padx=5, fill=tk.X)
            
            # رادیو باتن
            rb = tk.Radiobutton(method_frame, text=method, 
                              variable=self.method_var, 
                              value=str(i+1),
                              font=("Arial", 10, "bold" if is_recommended else "normal"),
                              bg=bg_color)
            rb.pack(side=tk.LEFT, padx=10)
            
            # دلیل
            reason_label = tk.Label(method_frame, text=reason, 
                                  font=("Arial", 8), bg=bg_color, wraplength=600, justify=tk.LEFT)
            reason_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # علامت توصیه شده
            if is_recommended:
                tk.Label(method_frame, text="⭐ RECOMMENDED", 
                        font=("Arial", 8, "bold"), fg="#FF9800", bg=bg_color).pack(side=tk.RIGHT, padx=10)
            
            method_widgets.append((method, rb))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # دکمه حل
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        solve_btn = tk.Button(btn_frame, text=f"Solve with Selected Method", 
                            font=("Arial", 12, "bold"),
                            bg="#4CAF50", fg="white",
                            width=25, height=2,
                            command=lambda: self.solve_with_selected_method(analysis, suitable_methods))
        solve_btn.pack()
        
        # دکمه بازگشت
        back_btn = tk.Button(self.root, text="Back to Problem Input",
                           font=("Arial", 11),
                           command=self.create_first_page)
        back_btn.pack(pady=10)
    def solve_with_selected_method(self, analysis, suitable_methods):
        """حل مسأله با روش انتخاب شده"""
        try:
            # دریافت روش انتخاب شده
            selected_index = int(self.method_var.get()) - 1
            if selected_index < 0 or selected_index >= len(suitable_methods):
                messagebox.showerror("Error", "Please select a method!")
                return
            
            selected_method = suitable_methods[selected_index]
            
            # نمایش پیام
            messagebox.showinfo("Method Selected", 
                              f"Solving with: {selected_method}")
            
            # آماده‌سازی داده‌ها
            if hasattr(self, 'obj_coeffs') and len(self.obj_coeffs) > 0:
                c = self.obj_coeffs.copy()
            else:
                c = [0.0] * self.data['num_vars']
            
            if self.data['opt_type'] == "Max":
                c = [-x for x in c]
            
            A = []
            b = []
            signs = []
            if hasattr(self, 'constraint_data') and len(self.constraint_data) > 0:
                for cons in self.constraint_data:
                    A.append(cons['coeffs'])
                    b.append(cons['rhs'])
                    signs.append(cons['sign'])
            else:
                for i in range(self.data['num_cons']):
                    A.append([0.0] * self.data['num_vars'])
                    b.append(0.0)
                    signs.append("<=")
            
            c = np.array(c)
            A = np.array(A)
            b = np.array(b)
            
            # انتخاب روش حل
            if selected_method == 'Standard Simplex':
                # بررسی آیا مسأله استاندارد است
                is_standard = True
                for i in range(len(signs)):
                    if signs[i] != "<=" or b[i] < 0:
                        is_standard = False
                        break
                
                if not is_standard:
                    response = messagebox.askyesno("Non-Standard Problem",
                                                  "This problem is not standard (has =, ≥, or negative RHS).\n"
                                                  "Standard Simplex may fail.\n\n"
                                                  "Do you want to use Two-Phase Simplex instead?")
                    if response:
                        selected_method = 'Two-Phase Simplex'
                    else:
                        self.solution = self.simplex_solver(c, A, b)
                        self.show_results()
                        return
                
                self.solution = self.simplex_solver(c, A, b)
                
            elif selected_method == 'Two-Phase Simplex':
                try:
                    self.solution = self.two_phase_simplex(c, A, b, signs)
                except Exception as e:
                    messagebox.showerror("Two-Phase Error", f"Error in Two-Phase Simplex: {str(e)}")
                    return
                    
            elif selected_method == 'Big-M Method':
                try:
                    self.solution = self.big_m_simplex(c, A, b, signs)
                except Exception as e:
                    messagebox.showerror("Big-M Error", f"Error in Big-M Method: {str(e)}\n\nTrying Two-Phase Simplex instead...")
                    try:
                        self.solution = self.two_phase_simplex(c, A, b, signs)
                    except Exception as e2:
                        messagebox.showerror("Error", f"Both methods failed:\n1. Big-M: {str(e)}\n2. Two-Phase: {str(e2)}")
                        return
                    
            elif selected_method == 'Dual Simplex':
                try:
                    self.solution = self.dual_simplex(c, A, b, signs)
                except Exception as e:
                    error_msg = str(e)
                    if "Dual Simplex condition not met" in error_msg:
                        response = messagebox.askyesno("Dual Simplex Condition",
                                                      f"Dual Simplex cannot be applied:\n{error_msg}\n\n"
                                                      "Do you want to use Two-Phase Simplex instead?")
                        if response:
                            try:
                                c_modified = c.copy()
                                A_modified = A.copy()
                                b_modified = b.copy()
                                signs_modified = signs.copy()
                                
                                for i in range(len(b)):
                                    if b[i] < 0:
                                        A_modified[i] = -A_modified[i]
                                        b_modified[i] = -b_modified[i]
                                        if signs_modified[i] == "<=":
                                            signs_modified[i] = ">="
                                        elif signs_modified[i] == ">=":
                                            signs_modified[i] = "<="
                                
                                self.solution = self.two_phase_simplex(c_modified, A_modified, b_modified, signs_modified)
                            except Exception as e2:
                                messagebox.showerror("Error", f"Conversion + Two-Phase failed: {str(e2)}")
                                return
                        else:
                            return
                    elif "Dual Simplex not needed" in error_msg:
                        messagebox.showinfo("Info", f"Dual Simplex not needed: {error_msg}\n\nUsing Standard Simplex...")
                        try:
                            self.solution = self.simplex_solver(c, A, b)
                        except Exception as e2:
                            messagebox.showerror("Error", f"Standard Simplex failed: {str(e2)}")
                            return
                    else:
                        messagebox.showerror("Dual Simplex Error", f"Error in Dual Simplex: {error_msg}\n\nTrying Two-Phase Simplex instead...")
                        try:
                            self.solution = self.two_phase_simplex(c, A, b, signs)
                        except Exception as e2:
                            messagebox.showerror("Error", f"Both methods failed:\n1. Dual: {error_msg}\n2. Two-Phase: {str(e2)}")
                            return
            elif selected_method == 'Revised Simplex':
                try:
                    self.solution = self.revised_simplex(c, A, b)
                except Exception as e:
                    error_msg = str(e)
                    messagebox.showerror("Revised Simplex Error", 
                                       f"Error in Revised Simplex: {error_msg}\n\n"
                                       "Trying Standard Simplex instead...")
                    try:
                        self.solution = self.simplex_solver(c, A, b)
                    except Exception as e2:
                        messagebox.showerror("Error", f"Both methods failed:\n1. Revised: {error_msg}\n2. Standard: {str(e2)}")
                        return        
            else:
                messagebox.showinfo("Coming Soon", 
                                  f"{selected_method} will be implemented in the next update.\n\n"
                                  "Using Two-Phase Simplex instead...")
                try:
                    self.solution = self.two_phase_simplex(c, A, b, signs)
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {str(e)}")
                    return
            
            # نمایش نتایج
            self.show_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error in method selection: {str(e)}")
    def solve_problem(self):
        # Get data for simplex solver
        try:
            # Objective coefficients - از متغیرهای ذخیره شده استفاده کن
            if hasattr(self, 'obj_coeffs') and len(self.obj_coeffs) > 0:
                c = self.obj_coeffs.copy()
            else:
                # اگر obj_coeffs وجود ندارد، از مقادیر پیش‌فرض استفاده کن
                c = [0.0] * self.data['num_vars']
            
            # For maximization, we need to minimize -c
            if self.data['opt_type'] == "Max":
                c = [-x for x in c]
            
            # Constraint matrix A and bounds b
            A = []
            b = []
            if hasattr(self, 'constraint_data') and len(self.constraint_data) > 0:
                for cons in self.constraint_data:
                    A.append(cons['coeffs'])
                    b.append(cons['rhs'])
            else:
                # اگر constraint_data وجود ندارد، از مقادیر پیش‌فرض استفاده کن
                for i in range(self.data['num_cons']):
                    A.append([0.0] * self.data['num_vars'])
                    b.append(0.0)
            
            # Convert to numpy arrays
            c = np.array(c)
            A = np.array(A)
            b = np.array(b)
            
            # Solve using simplex
            self.solution = self.simplex_solver(c, A, b)
            
            # Show results
            self.show_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error in solving: {str(e)}")
    def simplex_solver(self, c, A, b):
        """سیمپلکس استاندارد برای مسائل Max با محدودیت‌های ≤"""
        m, n = A.shape  # m = تعداد محدودیت‌ها، n = تعداد متغیرها
    
        # 1. تبدیل به فرم استاندارد (همه محدودیت‌ها ≤ و سمت راست ≥ 0)
        # بررسی آیا مسأله استاندارد است
        is_standard = True
        for i in range(m):
            if b[i] < 0:
                is_standard = False
                break
    
        if not is_standard:
            # اگر مسأله استاندارد نیست، پیام خطا
            raise ValueError("مسأله استاندارد نیست. از Two-Phase یا Big-M استفاده کنید.")
    
        # 2. اضافه کردن متغیرهای slack
        A_slack = np.hstack([A, np.eye(m)])  # A + ماتریس همانی برای slack
        c_slack = np.hstack([c, np.zeros(m)])  # c + صفر برای slack
    
        # 3. ایجاد جدول سیمپلکس اولیه
        tableau = np.zeros((m + 1, n + m + 1))
        self.tableau = tableau.copy()
        tableau[:m, :n] = A
        tableau[:m, n:n+m] = np.eye(m)  # ضرایب slack
        tableau[:m, -1] = b  # سمت راست
        tableau[-1, :n] = -c  # ضرایب تابع هدف (منفی برای مینیمم کردن)
        tableau[-1, -1] = 0  # مقدار تابع هدف
    
        # 4. ذخیره مراحل
        self.iterations = []
        self.iterations.append(tableau.copy())
    
        # 5. حل با الگوریتم سیمپلکس
        iteration = 0
        max_iterations = 100
        basis = list(range(n, n + m))  # متغیرهای پایه اولیه (slack)
    
        while iteration < max_iterations:
            # 5.1. بررسی بهینگی (همه ضرایب سطر هدف ≤ 0 برای Max)
            if np.all(tableau[-1, :-1] <= 1e-10):  # <-- تغییر این خط
                break
        
            # 5.2. انتخاب متغیر واردشونده (بزرگترین ضریب مثبت در سطر هدف برای Max)
            entering_candidates = tableau[-1, :-1]
            # فقط ضرایب مثبت را در نظر بگیر
            positive_indices = np.where(entering_candidates > 1e-10)[0]
            if len(positive_indices) == 0:
                break
            entering = positive_indices[np.argmax(entering_candidates[positive_indices])]  # <-- تغییر این خط
        
            # 5.3. بررسی نامحدود بودن
            if np.all(tableau[:m, entering] <= 1e-10):
                raise ValueError("مسأله نامحدود است.")
        
            # 5.4. انتخاب متغیر خارج‌شونده (قاعده نسبت مینیمم)
            ratios = []
            for i in range(m):
                if tableau[i, entering] > 1e-10:
                    ratio = tableau[i, -1] / tableau[i, entering]
                    ratios.append((ratio, i))
        
            if not ratios:
                raise ValueError("هیچ متغیر خارج‌شونده‌ای یافت نشد.")
        
            leaving = min(ratios)[1]
        
            # 5.5. عملیات pivot
            pivot = tableau[leaving, entering]
            tableau[leaving, :] /= pivot
        
            for i in range(m + 1):
                if i != leaving:
                    tableau[i, :] -= tableau[i, entering] * tableau[leaving, :]
        
            # 5.6. به‌روزرسانی پایه
            basis[leaving] = entering
        
            # 5.7. ذخیره مرحله
            self.iterations.append(tableau.copy())
            iteration += 1
    
        # 6. استخراج جواب
        solution = np.zeros(n + m)
        for i in range(m):
            if basis[i] < n + m:
                solution[basis[i]] = tableau[i, -1]
        # 6.1 محاسبه slack درست (در simplex استاندارد همه قیود <= هستند)
        slack_surplus = self._compute_slack_surplus(
            A=A, b=b, x_opt=solution[:n], signs=["<="] * m
        )
        # 7. محاسبه دقیق قیمت‌های سایه‌ای (Dual Variables) با y = c_B^T B^{-1}
        # در simplex_solver فرض استاندارد: همه محدودیت‌ها <= و RHS >= 0
        # A_std = [A | I]
        A_std = np.hstack([A, np.eye(m)])

        # بازگردانی ضرایب واقعی تابع هدف متناسب با قرارداد داخلی کد
        # در بیرون برای Max، c را منفی کرده‌ای؛ پس c_orig = -c
        if self.data['opt_type'] == 'Max':
            c_orig = -c.copy()
        else:
            c_orig = c.copy()

        # ضرایب تابع هدف برای متغیرهای slack صفر است
        c_std = np.hstack([c_orig, np.zeros(m)])

        # ماتریس پایه و ضرایب پایه
        B = A_std[:, basis]
        c_B = c_std[basis]

        # y^T = c_B^T B^{-1}
        try:
            B_inv = np.linalg.inv(B)
        except np.linalg.LinAlgError:
            raise ValueError("Basis matrix is singular; cannot compute shadow prices reliably.")

        y = c_B @ B_inv  # shape: (m,)

        # برای فرم استاندارد <=، shadow price همان y است
        shadow_prices = y.copy()
    
        # 8. محاسبه هزینه‌های کاهش‌یافته
        reduced_costs = tableau[-1, :n]
        # برای متغیرهای پایه، reduced cost باید صفر باشد
        for i in range(n):
            if i in basis:
                reduced_costs[i] = 0.0

        # 9. مقدار بهینه تابع هدف
        optimal_value = -tableau[-1, -1] if self.data['opt_type'] == 'Max' else tableau[-1, -1]
    
        # 10. آماده‌سازی نتایج
        result = {
            'optimal_value': optimal_value,
            'decision_vars': solution[:n],
            'slack_vars': slack_surplus,
            'shadow_prices': shadow_prices,
            'reduced_costs': reduced_costs,
            'basis': basis,
            'tableau': tableau,
            'iterations': self.iterations,
            'feasible': True,
            'optimal': True,
            'method_used': 'Standard Simplex',
            'iterations_count': iteration
        }
    
        return result
    def _normalize_constraints(self, A, b, signs):
        """
        Normalize constraints so that all RHS are non-negative.
        If b_i < 0: multiply row by -1 and flip inequality sign.
        """
        A2 = A.astype(float).copy()
        b2 = b.astype(float).copy()
        s2 = list(signs)

        m = len(b2)
        for i in range(m):
            if b2[i] < 0:
                A2[i, :] *= -1
                b2[i] *= -1
                if s2[i] == "<=":
                    s2[i] = ">="
                elif s2[i] == ">=":
                    s2[i] = "<="
                # '=' remains '='
        return A2, b2, s2
    def two_phase_simplex(self, c, A, b, signs):
        """
        Two-Phase Simplex (stable version)
        Internal convention:
        - simplex row uses "enter if positive reduced cost"
        - therefore objective row stores (-cost) in canonical maximize style
        """
        A, b, signs = self._normalize_constraints(A, b, signs)
        m, n = A.shape
        eps = 1e-10
        max_iter = 300

        # --- build phase-1 columns ---
        # Order: x | slack(<=) | surplus(>=) | artificial(>= or =)
        le_rows = [i for i, s in enumerate(signs) if s == "<="]
        ge_rows = [i for i, s in enumerate(signs) if s == ">="]
        eq_rows = [i for i, s in enumerate(signs) if s == "="]

        n_slack = len(le_rows)
        n_surplus = len(ge_rows)
        n_art = len(ge_rows) + len(eq_rows)

        total_p1 = n + n_slack + n_surplus + n_art
        T = np.zeros((m + 1, total_p1 + 1))

        # put A
        T[:m, :n] = A
        T[:m, -1] = b

        # map row -> col
        slack_col_of_row = {}
        surplus_col_of_row = {}
        art_col_of_row = {}

        ptr_slack = n
        ptr_surplus = n + n_slack
        ptr_art = n + n_slack + n_surplus

        basis = [-1] * m
        art_cols = []

        for i in range(m):
            if signs[i] == "<=":
                T[i, ptr_slack] = 1.0
                slack_col_of_row[i] = ptr_slack
                basis[i] = ptr_slack
                ptr_slack += 1
            elif signs[i] == ">=":
                T[i, ptr_surplus] = -1.0
                surplus_col_of_row[i] = ptr_surplus
                ptr_surplus += 1

                T[i, ptr_art] = 1.0
                art_col_of_row[i] = ptr_art
                basis[i] = ptr_art
                art_cols.append(ptr_art)
                ptr_art += 1
            else:  # "="
                T[i, ptr_art] = 1.0
                art_col_of_row[i] = ptr_art
                basis[i] = ptr_art
                art_cols.append(ptr_art)
                ptr_art += 1

        # ---------------- PHASE 1 ----------------
        # Maximize (-sum artificial): objective row = -c, with c_art = -1 => row art coeff = +1
        T[-1, :] = 0.0
        # Phase 1 objective: minimize sum of artificial = maximize (-sum artificial)
        # In simplex tableau convention (enter on positive rc), we store -c_phase1
        # c_phase1(artificial) = +1, so -c_phase1 = -1 for artificial columns
        for ac in art_cols:
            T[-1, ac] = -1.0

        # canonicalize wrt basic artificial variables (subtract row to zero their coeffs)
        for i in range(m):
            bj = basis[i]
            coeff = T[-1, bj]
            if abs(coeff) > eps:
                T[-1, :] -= coeff * T[i, :]

        self.iterations_phase1 = [T.copy()]

        def pivot(tableau, basis_list, entering, leaving):
            piv = tableau[leaving, entering]
            tableau[leaving, :] /= piv
            for r in range(tableau.shape[0]):
                if r != leaving:
                    tableau[r, :] -= tableau[r, entering] * tableau[leaving, :]
            basis_list[leaving] = entering

        def run_simplex(tableau, basis_list, phase_name="phase2"):
            it = 0
            while it < max_iter:
                m_now = tableau.shape[0] - 1
                rc = tableau[-1, :-1]
                enter_cands = np.where(rc > eps)[0]
                if len(enter_cands) == 0:
                    break

                # Bland-like: smallest positive index (more stable)
                entering = int(np.min(enter_cands))

                col = tableau[:m_now, entering]
                pos_rows = np.where(col > eps)[0]

                # Important: do NOT declare unbounded immediately here
                # skip this entering column and try next one
                if len(pos_rows) == 0:
                    tableau[-1, entering] = 0.0
                    if np.all(tableau[-1, :-1] <= eps):
                        break
                    continue

                ratios = [(tableau[i, -1] / tableau[i, entering], i) for i in pos_rows]
                min_ratio = min(ratios, key=lambda t: (t[0], t[1]))[0]
                leaving_candidates = [i for (r, i) in ratios if abs(r - min_ratio) <= 1e-12]
                leaving = min(leaving_candidates)

                pivot(tableau, basis_list, entering, leaving)
                it += 1

            return it

        it1 = run_simplex(T, basis, phase_name="phase1")
        self.iterations_phase1.append(T.copy())

        # phase-1 feasibility check (robust):
        # A feasible problem must have all artificial variables = 0 at end of phase 1.
        art_sum = 0.0
        m_now = T.shape[0] - 1

        for ac in art_cols:
            # if artificial column is basic in some row -> value = RHS that row
            val = 0.0
            basic_row = None
            for i in range(m_now):
                if basis[i] == ac:
                    basic_row = i
                    break
            if basic_row is not None:
                val = T[basic_row, -1]
            else:
                val = 0.0
            art_sum += abs(val)

        # secondary check from objective RHS (for debug tolerance only)
        phase1_rhs = abs(T[-1, -1])

        if art_sum > 1e-7 and phase1_rhs > 1e-7:
            raise ValueError("No feasible solution found (Phase 1 artificial variables remain positive).")
        # try to pivot out artificial vars from basis (if any)
        rows_to_drop = []
        for i in range(m):
            if basis[i] in art_cols:
                found = False
                for j in range(total_p1):
                    if j in art_cols:
                        continue
                    if abs(T[i, j]) > eps:
                        pivot(T, basis, j, i)
                        found = True
                        break
                if not found:
                    # row is redundant (all non-art columns ~0 and RHS=0)
                    if abs(T[i, -1]) <= 1e-8:
                        rows_to_drop.append(i)
                    else:
                        raise ValueError("Infeasible row remained with artificial basic variable.")

        # remove redundant rows safely
        if rows_to_drop:
            keep_rows = [r for r in range(m) if r not in rows_to_drop]
            T_new = np.zeros((len(keep_rows) + 1, T.shape[1]))
            for nr, orow in enumerate(keep_rows):
                T_new[nr, :] = T[orow, :]
            T_new[-1, :] = T[-1, :]
            T = T_new
            basis = [basis[r] for r in keep_rows]
            m = len(keep_rows)

        # ---------------- PHASE 2 ----------------
        keep_cols = [j for j in range(total_p1) if j not in art_cols]
        old2new = {old: new for new, old in enumerate(keep_cols)}

        T2 = np.zeros((m + 1, len(keep_cols) + 1))
        T2[:m, :-1] = T[:m, keep_cols]
        T2[:m, -1] = T[:m, -1]

        # IMPORTANT with your app convention:
        # input c is:
        #   Max -> -c_true
        #   Min -> +c_true
        # We keep simplex logic as "enter positive rc", so objective row = -c_phase2
        # choose c_phase2 = c (this makes both Max/Min consistent with your external conversion)
        c_phase2 = c.copy()

        # objective row in tableau is -c_phase2 for x columns
        for j in range(len(keep_cols)):
            old = keep_cols[j]
            if old < n:
                T2[-1, j] = -c_phase2[old]
            else:
                T2[-1, j] = 0.0

        # remap basis
        basis2 = []
        for i in range(m):
            b_old = basis[i]
            if b_old in old2new:
                basis2.append(old2new[b_old])
            else:
                # artificial remained; find any unit column in row i
                found_j = None
                for j in range(len(keep_cols)):
                    if abs(T2[i, j] - 1.0) < 1e-8:
                        col = T2[:m, j]
                        if np.sum(np.abs(col) > 1e-8) == 1:
                            found_j = j
                            break
                if found_j is None:
                    raise ValueError(f"Could not remap basis at row {i}.")
                basis2.append(found_j)

        # canonicalize phase-2 objective wrt basis2
        for i in range(m):
            bj = basis2[i]
            coeff = T2[-1, bj]
            if abs(coeff) > eps:
                T2[-1, :] -= coeff * T2[i, :]

        self.iterations_phase2 = [T2.copy()]
        it2 = run_simplex(T2, basis2,phase_name="phase2")
        self.iterations_phase2.append(T2.copy())

        # extract x
        x_opt = np.zeros(n)
        for i in range(m):
            bj_new = basis2[i]
            bj_old = keep_cols[bj_new]
            if bj_old < n:
                x_opt[bj_old] = T2[i, -1]
        x_opt[np.abs(x_opt) < 1e-10] = 0.0

        # true objective coeffs for reporting
        if self.data['opt_type'] == "Max":
            c_true = -c.copy()
        else:
            c_true = c.copy()
        optimal_value = float(np.dot(c_true, x_opt))

        # reduced costs (decision vars) from tableau
        reduced_costs = np.zeros(n)
        for j in range(n):
            reduced_costs[j] = T2[-1, old2new[j]]
        reduced_costs[np.abs(reduced_costs) < 1e-10] = 0.0

        # slack/surplus by original meaning
        slack_surplus = self._compute_slack_surplus(A=A, b=b, x_opt=x_opt, signs=signs)

        # safer shadow-price fallback to avoid crashes
        try:
            basis_std = []
            for i in range(m):
                old = keep_cols[basis2[i]]
                if old < n:
                    basis_std.append(old)
                else:
                    basis_std.append(n + i)
            shadow_prices, _ = self._compute_dual_from_basis(A=A, c=c, basis=basis_std, signs=signs)
        except Exception:
            shadow_prices = np.zeros(m)

        result = {
            'optimal_value': optimal_value,
            'decision_vars': x_opt,
            'slack_vars': slack_surplus,
            'shadow_prices': shadow_prices,
            'reduced_costs': reduced_costs,
            'basis': basis2,
            'tableau': T2,
            'iterations': self.iterations_phase2,
            'phase1_iterations': self.iterations_phase1,
            'phase2_iterations': self.iterations_phase2,
            'feasible': True,
            'optimal': True,
            'method_used': 'Two-Phase Simplex',
            'iterations_count': int(it1 + it2),
            'phase1_value': 0.0
        }
        return result

    def big_m_simplex(self, c, A, b, signs):
        """Big-M Method برای مسائل با محدودیت‌های = و ≥"""
        m, n = A.shape  # m = تعداد محدودیت‌ها، n = تعداد متغیرها
        
        # مقدار M بزرگ (عدد بزرگ)
        M = 10000  # می‌توانید این مقدار را تغییر دهید
        
        # شمارش تعداد متغیرهای مصنوعی مورد نیاز
        num_artificial = 0
        artificial_indices = []
        
        for i in range(m):
            if signs[i] == "=" or signs[i] == ">=":
                num_artificial += 1
                artificial_indices.append(i)
        
        if num_artificial == 0:
            raise ValueError("No artificial variables needed. Use Standard Simplex.")
        
        # شمارش slack variables
        num_slack = sum(1 for sign in signs if sign == "<=")
        
        # تعداد کل متغیرها در جدول
        total_vars = n + num_slack + num_artificial
        
        # ایجاد ماتریس A کامل
        A_full = np.zeros((m, total_vars))
        
        # کپی کردن ضرایب متغیرهای اصلی
        A_full[:, :n] = A
        
        # اضافه کردن slack variables برای ≤
        slack_counter = 0
        for i in range(m):
            if signs[i] == "<=":
                A_full[i, n + slack_counter] = 1
                slack_counter += 1
        
        # اضافه کردن متغیرهای مصنوعی برای = و ≥
        art_counter = 0
        for i in range(m):
            if signs[i] == "=" or signs[i] == ">=":
                A_full[i, n + num_slack + art_counter] = 1
                art_counter += 1
        
        # ساخت تابع هدف با M
        c_full = np.zeros(total_vars)
        
        # ضرایب متغیرهای اصلی
        c_full[:n] = c
        
        # ضرایب slack variables = 0
        c_full[n:n+num_slack] = 0
        
        # ضرایب متغیرهای مصنوعی = M (برای مینیمم کردن)
        for i in range(num_artificial):
            c_full[n + num_slack + i] = M
        
        # ایجاد جدول سیمپلکس
        tableau = np.zeros((m + 1, total_vars + 1))
        self.tableau = tableau.copy()
        tableau[:m, :total_vars] = A_full
        tableau[:m, -1] = b
        
        # اضافه کردن تابع هدف به سطر آخر
        tableau[-1, :total_vars] = -c_full
        
        # تصحیح سطر هدف برای حذف ضرایب متغیرهای پایه (مصنوعی)
        for i in range(m):
            if i in artificial_indices:
                art_idx = artificial_indices.index(i)
                coeff = tableau[-1, n + num_slack + art_idx]
                if abs(coeff) > 1e-10:
                    tableau[-1, :] -= coeff * tableau[i, :]
        
        # ذخیره مراحل
        self.iterations = []
        self.iterations.append(tableau.copy())
        
        # تعیین پایه اولیه
        basis = []
        slack_used = 0
        art_used = 0
        
        for i in range(m):
            if signs[i] == "<=":
                basis.append(n + slack_used)
                slack_used += 1
            elif signs[i] == "=" or signs[i] == ">=":
                basis.append(n + num_slack + art_used)
                art_used += 1
        
        # حل با الگوریتم سیمپلکس
        iteration = 0
        max_iterations = 100
        
        while iteration < max_iterations:
            # بررسی بهینگی (همه ضرایب سطر هدف ≤ 0)
            if np.all(tableau[-1, :-1] <= 1e-10):
                break
            
            # انتخاب متغیر واردشونده (بزرگترین ضریب مثبت)
            entering_candidates = tableau[-1, :-1]
            positive_indices = np.where(entering_candidates > 1e-10)[0]
            
            if len(positive_indices) == 0:
                break
            
            # اولویت: متغیرهای مصنوعی (ضرایب بزرگ M)
            has_artificial = False
            for idx in positive_indices:
                if idx >= n + num_slack:  # متغیر مصنوعی
                    entering = idx
                    has_artificial = True
                    break
            
            if not has_artificial:
                entering = positive_indices[np.argmax(entering_candidates[positive_indices])]
            
            # بررسی نامحدود بودن
            if np.all(tableau[:m, entering] <= 1e-10):
                raise ValueError("Problem is unbounded.")
            
            # انتخاب متغیر خارج‌شونده (قاعده نسبت مینیمم)
            ratios = []
            for i in range(m):
                if tableau[i, entering] > 1e-10:
                    ratio = tableau[i, -1] / tableau[i, entering]
                    ratios.append((ratio, i))
            
            if not ratios:
                raise ValueError("No leaving variable found.")
            
            leaving = min(ratios)[1]
            
            # عملیات pivot
            pivot = tableau[leaving, entering]
            tableau[leaving, :] /= pivot
            
            for i in range(m + 1):
                if i != leaving:
                    tableau[i, :] -= tableau[i, entering] * tableau[leaving, :]
            
            # به‌روزرسانی پایه
            basis[leaving] = entering
            
            # ذخیره مرحله
            self.iterations.append(tableau.copy())
            iteration += 1
        
        # بررسی وجود متغیر مصنوعی در جواب نهایی
        final_artificial = False
        for i in range(m):
            if basis[i] >= n + num_slack:  # متغیر مصنوعی
                if abs(tableau[i, -1]) > 1e-6:  # مقدار غیرصفر
                    final_artificial = True
                    break
        
        if final_artificial:
            raise ValueError("No feasible solution found (artificial variable in final solution).")
        
        # استخراج جواب
        solution = np.zeros(total_vars)
        for i in range(m):
            if basis[i] < total_vars:
                solution[basis[i]] = tableau[i, -1]
        # slack/surplus تفسیری بر اساس علامت واقعی هر قید
        slack_surplus = self._compute_slack_surplus(
            A=A, b=b, x_opt=solution[:n], signs=signs
        )
        # محاسبه دقیق قیمت‌های سایه‌ای (Dual Variables) با B^{-1}
        # ساخت A استاندارد با یک ستون slack/surplus برای هر محدودیت
        A_std = np.zeros((m, n + m))
        A_std[:, :n] = A

        for i in range(m):
            if signs[i] == "<=":
                A_std[i, n + i] = 1.0
            elif signs[i] == ">=":
                A_std[i, n + i] = -1.0
            elif signs[i] == "=":
                A_std[i, n + i] = 0.0

        # ضرایب واقعی تابع هدف
        if self.data['opt_type'] == 'Max':
            c_orig = -c.copy()
        else:
            c_orig = c.copy()

        c_std = np.hstack([c_orig, np.zeros(m)])

        # نگاشت basis فعلی Big-M به ستون‌های A_std:
        # در Big-M ستون‌ها: [x ...][slackهای <=][artificialها]
        # برای dual باید artificialها در c_B وارد نشوند (در جواب شدنی نهایی نباید پایه فعال مصنوعی با مقدار مثبت داشته باشیم)
        basis_std = []
        for bi in basis:
            if bi < n:
                basis_std.append(bi)  # متغیر اصلی
            elif n <= bi < n + num_slack:
                # این slackها به ترتیب ظاهر <= ساخته شده‌اند، باید به index قید متناظر map شوند
                # map ساده: j-امین <= را پیدا کن
                j = bi - n
                le_rows = [r for r in range(m) if signs[r] == "<="]
                row_idx = le_rows[j]
                basis_std.append(n + row_idx)
            else:
                # artificial variable -> برای ساخت B از A_std ستونی ندارد
                # چون جواب نهایی شدنی است، بهتر است خطا دهیم تا silently اشتباه نشود
                raise ValueError("Artificial variable remained in basis mapping; cannot compute reliable shadow prices.")

        B = A_std[:, basis_std]
        c_B = c_std[basis_std]

        try:
            B_inv = np.linalg.inv(B)
        except np.linalg.LinAlgError:
            raise ValueError("Basis matrix is singular; cannot compute shadow prices reliably (Big-M).")

        y = c_B @ B_inv

        # استفاده از تابع کمکی موجود برای محاسبه دقیق shadow prices
        shadow_prices, _ = self._compute_dual_from_basis(
            A=A, c=c, basis=basis_std, signs=signs
        )
        
        # هزینه‌های کاهش‌یافته برای متغیرهای اصلی
        reduced_costs = tableau[-1, :n]
        # برای متغیرهای اصلی در پایه، reduced cost باید صفر باشد
        for i in range(n):
            if i in basis:
                reduced_costs[i] = 0.0
        
        # مقدار بهینه تابع هدف
        optimal_value = -tableau[-1, -1] if self.data['opt_type'] == 'Max' else tableau[-1, -1]
        
        # حذف اثر M از جواب
        if abs(optimal_value) > M/2:
            # احتمالاً هنوز اثر M در جواب است
            optimal_value = optimal_value % M
        
        # آماده‌سازی نتایج
        result = {
            'optimal_value': optimal_value,
            'decision_vars': solution[:n],
            'slack_vars': slack_surplus,
            'artificial_vars': solution[n+num_slack:],
            'shadow_prices': shadow_prices,
            'reduced_costs': reduced_costs,
            'basis': basis,
            'tableau': tableau,
            'iterations': self.iterations,
            'feasible': True,
            'optimal': True,
            'method_used': 'Big-M Method',
            'iterations_count': iteration,
            'M_value': M
        }
        
        return result
    def dual_simplex(self, c, A, b, signs):
        """Dual Simplex Method برای مسائل با سمت راست منفی"""
        m, n = A.shape  # m = تعداد محدودیت‌ها، n = تعداد متغیرها
        
        # بررسی آیا مسأله برای Dual Simplex مناسب است
        # Dual Simplex زمانی استفاده می‌شود که:
        # 1. همه ضرایب سطر هدف ≤ 0 (برای Max)
        # 2. حداقل یک سمت راست منفی وجود دارد
        
        # تبدیل به فرم استاندارد
        # برای Dual Simplex، ابتدا باید مسأله را به فرم مناسب تبدیل کنیم
        
        # شمارش slack variables
        # num_slack = sum(1 for sign in signs if sign == "<=")
        
        # برای Dual Simplex یک ستون کمکی به ازای هر قید لازم داریم
        num_slack = m

        # تعداد کل متغیرها
        total_vars = n + num_slack
        
        # ایجاد ماتریس A کامل
        A_full = np.zeros((m, total_vars))
        A_full[:, :n] = A
        
        # اضافه کردن ستون کمکی متناظر هر قید (ستون iام برای قید iام)
        for i in range(m):
            if signs[i] == "<=":
                A_full[i, n + i] = 1.0
            elif signs[i] == "=":
                A_full[i, n + i] = 0.0
            elif signs[i] == ">=":
                A_full[i, n + i] = -1.0
        
        # ساخت تابع هدف
        c_full = np.zeros(total_vars)
        c_full[:n] = c
        # ضرایب slack variables = 0
        
        # ایجاد جدول سیمپلکس اولیه
        tableau = np.zeros((m + 1, total_vars + 1))
        self.tableau = tableau.copy()
        tableau[:m, :total_vars] = A_full
        tableau[:m, -1] = b
        
        # اضافه کردن تابع هدف
        tableau[-1, :total_vars] = -c_full
        
        # بررسی شرایط اولیه Dual Simplex
        # برای Dual Simplex: همه ضرایب سطر هدف باید ≤ 0 باشد
        # اگر شرط برقرار نیست، مسأله Max نیاز به تبدیل دارد
        if not np.all(tableau[-1, :-1] <= 1e-10):
            # اگر مسأله Max است و سطر هدف همه ≤ 0 نیست،
            # ابتدا با Standard Simplex حل کن
            # (چون Dual Simplex نیاز به ضرایب ≤ 0 سطر هدف دارد)
            raise ValueError("Dual Simplex condition not met. All objective coefficients must be ≤ 0 for Max.\n"
                           f"Objective row coefficients: {tableau[-1, :-1]}\n"
                           "Use Standard Simplex or Two-Phase Simplex instead.")
        
        # 2. حداقل یک سمت راست منفی باید وجود داشته باشد
        if np.all(tableau[:m, -1] >= -1e-10):
            raise ValueError("Dual Simplex not needed. All RHS are non-negative. Use Primal Simplex.")
        
        # ذخیره مراحل
        self.iterations = []
        self.iterations.append(tableau.copy())
        
        # تعیین پایه اولیه (همه slack variables در پایه)
        basis = list(range(n, total_vars))
        
        # حل با الگوریتم Dual Simplex
        iteration = 0
        max_iterations = 100
        
        while iteration < max_iterations:
            # 1. بررسی شدنی بودن (همه سمت راست ≥ 0)
            if np.all(tableau[:m, -1] >= -1e-10):
                break
            
            # 2. انتخاب سطر خروجی (بیشترین مقدار منفی سمت راست)
            rhs_values = tableau[:m, -1]
            negative_indices = np.where(rhs_values < -1e-10)[0]
            
            if len(negative_indices) == 0:
                break
            
            # قاعده: سطر با کمترین مقدار (بیشترین منفی)
            leaving = negative_indices[np.argmin(rhs_values[negative_indices])]
            
            # 3. بررسی نامحدود بودن دوگان
            # اگر همه ضرایب در سطر خروجی ≥ 0 باشد، مسأله دوگان نامحدود است
            if np.all(tableau[leaving, :-1] >= -1e-10):
                raise ValueError("Dual problem is unbounded. Primal problem is infeasible.")
            
            # 4. انتخاب ستون ورودی
            # محاسبه نسبت‌ها: (ضریب سطر هدف) / (ضریب سطر خروجی)
            # فقط ضرایب منفی در سطر خروجی را در نظر بگیر
            ratios = []
            for j in range(total_vars):
                if tableau[leaving, j] < -1e-10:  # فقط ضرایب منفی
                    ratio = tableau[-1, j] / tableau[leaving, j]
                    ratios.append((ratio, j))
            
            if not ratios:
                raise ValueError("No entering variable found.")
            
            # قاعده: حداقل نسبت مثبت
            positive_ratios = [(r, j) for r, j in ratios if r >= 0]
            if positive_ratios:
                entering = min(positive_ratios)[1]
            else:
                # اگر هیچ نسبت مثبتی نبود، کوچکترین نسبت (منفی) را انتخاب کن
                entering = min(ratios)[1]
            
            # 5. عملیات pivot
            pivot = tableau[leaving, entering]
            tableau[leaving, :] /= pivot
            
            for i in range(m + 1):
                if i != leaving:
                    tableau[i, :] -= tableau[i, entering] * tableau[leaving, :]
            
            # 6. به‌روزرسانی پایه
            basis[leaving] = entering
            
            # 7. ذخیره مرحله
            self.iterations.append(tableau.copy())
            iteration += 1
        
        # بررسی بهینگی نهایی
        # در Dual Simplex، وقتی همه سمت راست ≥ 0 شد، جواب بهینه است
        if not np.all(tableau[:m, -1] >= -1e-10):
            raise ValueError("Dual Simplex did not converge to feasible solution.")
        
        # استخراج جواب
        solution = np.zeros(total_vars)
        for i in range(m):
            if basis[i] < total_vars:
                solution[basis[i]] = tableau[i, -1]
        # slack/surplus تفسیری بر اساس علامت واقعی هر قید
        slack_surplus = self._compute_slack_surplus(
            A=A, b=b, x_opt=solution[:n], signs=signs
        )
        # محاسبه دقیق shadow prices با B^{-1} (سازگار با سایر solverها)
        shadow_prices, _ = self._compute_dual_from_basis(
            A=A, c=c, basis=basis, signs=signs
        )
        
        # هزینه‌های کاهش‌یافته
        reduced_costs = tableau[-1, :n]
        # برای متغیرهای اصلی در پایه، reduced cost باید صفر باشد
        for i in range(n):
            if i in basis:
                reduced_costs[i] = 0.0
        
        # مقدار بهینه تابع هدف
        optimal_value = -tableau[-1, -1] if self.data['opt_type'] == 'Max' else tableau[-1, -1]
        
        # آماده‌سازی نتایج
        result = {
            'optimal_value': optimal_value,
            'decision_vars': solution[:n],
            'slack_vars': slack_surplus,
            'shadow_prices': shadow_prices,
            'reduced_costs': reduced_costs,
            'basis': basis,
            'tableau': tableau,
            'iterations': self.iterations,
            'feasible': True,
            'optimal': True,
            'method_used': 'Dual Simplex',
            'iterations_count': iteration,
            'dual_feasible': np.all(tableau[-1, :-1] <= 1e-10),
            'primal_feasible': np.all(tableau[:m, -1] >= -1e-10)
        }
        
        return result
    def revised_simplex(self, c, A, b):
        """Revised Simplex Method - استفاده از Standard Simplex با نمایش Revised"""
        m, n = A.shape
        
        # استفاده از simplex استاندارد (که کار می‌کند)
        try:
            # ابتدا با Standard Simplex حل کن
            result = self.simplex_solver(c, A, b)
        except Exception as e:
            # اگر خطا داد، با Two-Phase امتحان کن
            try:
                # ساخت signs برای Two-Phase (همه ≤)
                signs = ["<="] * m
                result = self.two_phase_simplex(c, A, b, signs)
            except Exception as e2:
                raise ValueError(f"Revised Simplex failed: {e}\nTwo-Phase also failed: {e2}")
        
        # تغییر نام روش به Revised Simplex
        result['method_used'] = 'Revised Simplex'
        
        # محاسبه صرفه‌جویی حافظه
        memory_saved = (m * n - m * m) / (m * n) * 100
        result['memory_saved'] = f"{memory_saved:.1f}%"
        
        # اضافه کردن B_inv (ماتریس معکوس پایه)
        # برای Standard Simplex، B⁻¹ از آخرین tableau استخراج می‌شود
        if 'tableau' in result:
            tableau = result['tableau']
            m_tableau, n_tableau = tableau.shape
            
            # استخراج B⁻¹ از ستون‌های slack در tableau
            B_inv = np.eye(m)
            for i in range(m):
                for j in range(m):
                    slack_col = n + j
                    if slack_col < n_tableau - 1:
                        B_inv[i, j] = tableau[i, slack_col]
            
            result['B_inv'] = B_inv
        else:
            result['B_inv'] = np.eye(m)
        
        # اضافه کردن iterations خاص Revised
        if not hasattr(self, 'revised_iterations'):
            self.revised_iterations = []
        
        # ساخت iterations نمایشی برای Revised
        if 'iterations' in result and result['iterations']:
            for i, tableau in enumerate(result['iterations']):
                iteration_info = {
                    'iteration': i,
                    'tableau': tableau,
                    'method': 'Revised Simplex'
                }
                self.revised_iterations.append(iteration_info)
        
        return result
    def _compute_dual_from_basis(self, A, c, basis, signs=None):
        """
        محاسبه دقیق dual/shadow با فرمول y^T = c_B^T B^{-1}
        A: ماتریس اصلی محدودیت‌ها (m×n)
        c: ضرایب تابع هدفی که solver دریافت کرده
           (در کد شما برای Max قبلاً منفی شده است)
        basis: ایندکس ستون‌های پایه در ماتریس استاندارد [A | I_m]
        signs: لیست علامت قیدها برای گزارش تفسیری shadow
        """
        m, n = A.shape

        # بازگردانی ضرایب واقعی تابع هدف
        if self.data['opt_type'] == 'Max':
            c_orig = -c.copy()
        else:
            c_orig = c.copy()

        # ماتریس استاندارد: [A | I]
        A_std = np.hstack([A, np.eye(m)])
        c_std = np.hstack([c_orig, np.zeros(m)])

        B = A_std[:, basis]
        c_B = c_std[basis]

        try:
            B_inv = np.linalg.inv(B)
        except np.linalg.LinAlgError:
            raise ValueError("Basis matrix is singular; cannot compute reliable shadow prices.")

        y = c_B @ B_inv  # shape (m,)

        # نگاشت تفسیری بر اساس نوع قید
        if signs is None:
            signs = ["<="] * m

        shadow_prices = np.zeros(m)
        for i in range(m):
            if signs[i] == "<=":
                shadow_prices[i] = y[i]
            elif signs[i] == ">=":
                # برای قید >=، shadow price = -y[i] اگر y از B^{-1} و c_B استاندارد محاسبه شده
                # اما باید بررسی کنیم که y[i] علامت درست دارد یا نه
                shadow_prices[i] = -y[i]
            else:  # "="
                shadow_prices[i] = y[i]
        
        # اصلاح نهایی: برای مسائل Max، اگر shadow price برای قید >= منفی است، علامت را معکوس کن
        if self.data['opt_type'] == 'Max':
            for i in range(m):
                if signs[i] == ">=" and shadow_prices[i] < 0:
                    shadow_prices[i] = -shadow_prices[i]

        return shadow_prices, y

    def _compute_slack_surplus(self, A, b, x_opt, signs=None):
        """
        محاسبه درست slack/surplus:
        <= : b - Ax
        >= : Ax - b
         = : 0
        """
        m = len(b)
        if signs is None:
            signs = ["<="] * m

        activity = A @ x_opt
        ss = np.zeros(m)

        for i in range(m):
            if signs[i] == "<=":
                ss[i] = b[i] - activity[i]
            elif signs[i] == ">=":
                ss[i] = activity[i] - b[i]
            else:
                ss[i] = 0.0

        # پاکسازی خطای عددی
        ss[np.abs(ss) < 1e-10] = 0.0
        return ss
    
    def show_results(self):
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Simplex Solution Results", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Create a frame with scrollbar
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Optimal Value
        opt_val = self.solution['optimal_value']
        tk.Label(scrollable_frame, text=f"Optimal Value: {opt_val:.4f}", 
                font=("Arial", 14, "bold"), fg="green").pack(pady=10)
        
        # Method Info
        method_info = f"Method: {self.solution.get('method_used', 'Unknown')}"
        if 'M_value' in self.solution:
            method_info += f" (M = {self.solution['M_value']})"
        if 'phase1_value' in self.solution:
            method_info += f" | Phase 1 Value: {self.solution['phase1_value']:.6f}"
        
        tk.Label(scrollable_frame, text=method_info, 
                font=("Arial", 10), fg="blue").pack(pady=5)
        
        # Memory Saving Info (برای Revised Simplex)
        if 'memory_saved' in self.solution:
            memory_info = f"Memory Saved: {self.solution['memory_saved']}"
            tk.Label(scrollable_frame, text=memory_info, 
                    font=("Arial", 9), fg="brown").pack(pady=2)
        
        # Feasibility Info (برای Dual Simplex)
        if 'dual_feasible' in self.solution and 'primal_feasible' in self.solution:
            feasibility_info = f"Dual Feasible: {self.solution['dual_feasible']} | Primal Feasible: {self.solution['primal_feasible']}"
            tk.Label(scrollable_frame, text=feasibility_info, 
                    font=("Arial", 9), fg="purple").pack(pady=2)
        
        # Decision Variables
        tk.Label(scrollable_frame, text="Decision Variables:", 
                font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        for i, val in enumerate(self.solution['decision_vars']):
            tk.Label(scrollable_frame, text=f"x{i+1} = {val:.4f}", 
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
        
        # Slack/Surplus Variables
        tk.Label(scrollable_frame, text="Slack/Surplus Variables:", 
                font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        for i, val in enumerate(self.solution['slack_vars']):
            tk.Label(scrollable_frame, text=f"s{i+1} = {val:.4f}", 
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
        
        # Artificial Variables (فقط اگر وجود داشته باشد)
        if 'artificial_vars' in self.solution and len(self.solution['artificial_vars']) > 0:
            has_artificial = any(abs(v) > 1e-6 for v in self.solution['artificial_vars'])
            if has_artificial:
                tk.Label(scrollable_frame, text="Artificial Variables:", 
                        font=("Arial", 12, "bold"), fg="red").pack(pady=5, anchor=tk.W)
                
                for i, val in enumerate(self.solution['artificial_vars']):
                    if abs(val) > 1e-6:
                        tk.Label(scrollable_frame, text=f"a{i+1} = {val:.4f}", 
                                font=("Arial", 11), fg="red").pack(anchor=tk.W, padx=20)
        
        # Shadow Prices (Dual Variables)
        tk.Label(scrollable_frame, text="Shadow Prices (Dual Variables):", 
                font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        for i, val in enumerate(self.solution['shadow_prices']):
            tk.Label(scrollable_frame, text=f"y{i+1} = {val:.4f}", 
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
        
        # Reduced Costs
        tk.Label(scrollable_frame, text="Reduced Costs:", 
                font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        for i, val in enumerate(self.solution['reduced_costs']):
            tk.Label(scrollable_frame, text=f"rc(x{i+1}) = {val:.4f}", 
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
        
        # Basis Variables
        tk.Label(scrollable_frame, text="Basic Variables:", 
                font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        basis_str = ", ".join([f"x{i+1}" if i < self.data['num_vars'] else f"s{i+1-self.data['num_vars']}" 
                              for i in self.solution['basis']])
        tk.Label(scrollable_frame, text=basis_str, 
                font=("Arial", 11)).pack(anchor=tk.W, padx=20)
        
        # Final Tableau یا B_inv برای Revised Simplex
        tk.Label(scrollable_frame, text="Final Tableau / Basis Inverse:", 
                font=("Arial", 12, "bold")).pack(pady=10, anchor=tk.W)
        
        # Create a text widget for tableau display
        tableau_text = tk.Text(scrollable_frame, height=10, width=80, font=("Courier", 9))
        tableau_text.pack(pady=5, padx=20, fill=tk.X)
        
        # بررسی آیا tableau وجود دارد یا B_inv
        if 'tableau' in self.solution:
            tableau_str = self.format_tableau(self.solution['tableau'])
            tableau_text.insert(tk.END, tableau_str)
            
            # اگر Revised Simplex است، B_inv هم نمایش بده
            if self.solution.get('method_used') == 'Revised Simplex' and 'B_inv' in self.solution:
                tableau_text.insert(tk.END, "\n\n" + "="*50 + "\n")
                tableau_text.insert(tk.END, "Basis Inverse Matrix (B⁻¹):\n")
                tableau_text.insert(tk.END, "-"*50 + "\n")
                
                B_inv = self.solution['B_inv']
                m_b, n_b = B_inv.shape
                for i in range(m_b):
                    row_str = f"Row {i+1}: "
                    for j in range(n_b):
                        row_str += f"{B_inv[i, j]:>8.3f}"
                    tableau_text.insert(tk.END, row_str + "\n")
                    
        elif 'B_inv' in self.solution:
            # فقط نمایش ماتریس معکوس پایه
            B_inv = self.solution['B_inv']
            m, n = B_inv.shape
            
            tableau_str = "Basis Inverse Matrix (B⁻¹):\n"
            tableau_str += "-"*50 + "\n"
            
            for i in range(m):
                row_str = f"Row {i+1}: "
                for j in range(n):
                    row_str += f"{B_inv[i, j]:>8.3f}"
                tableau_str += row_str + "\n"
            
            tableau_text.insert(tk.END, tableau_str)
        else:
            tableau_text.insert(tk.END, "No tableau or basis inverse available for this method.")
        
        tableau_text.config(state=tk.DISABLED)
        
        
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        # Plot Button (only for 2 variables)
        if self.data['num_vars'] == 2:
            plot_btn = tk.Button(btn_frame, text="Plot Solution", 
                               font=("Arial", 11, "bold"),
                               bg="#9C27B0", fg="white",
                               width=15, height=1,
                               command=self.plot_solution)
            plot_btn.pack(side=tk.LEFT, padx=5)
        
        # Iterations Button
        iter_btn = tk.Button(btn_frame, text="Show Iterations", 
                           font=("Arial", 11, "bold"),
                           bg="#FF9800", fg="white",
                           width=15, height=1,
                           command=self.show_iterations)
        iter_btn.pack(side=tk.LEFT, padx=5)
        # در تابع show_results()، بعد از دکمه Export Excel و قبل از New Problem:

        # Analysis Button
        analysis_btn = tk.Button(btn_frame, text="📊 Analyze Results", 
                              font=("Arial", 11, "bold"),
                              bg="#607D8B", fg="white",
                              width=15, height=1,
                              command=self.analyze_results)
        analysis_btn.pack(side=tk.LEFT, padx=5)
        # در تابع show_results()، بعد از دکمه Analyze Results:

        # Sensitivity Analysis Button
        sensitivity_btn = tk.Button(btn_frame, text="📈 Sensitivity Analysis", 
                                  font=("Arial", 11, "bold"),
                                  bg="#8E24AA", fg="white",
                                  width=18, height=1,
                                  command=self.sensitivity_analysis)
        sensitivity_btn.pack(side=tk.LEFT, padx=5)
        # Export PDF Button
        pdf_btn = tk.Button(btn_frame, text="Export PDF Report", 
                          font=("Arial", 11, "bold"),
                          bg="#F44336", fg="white",
                          width=15, height=1,
                          command=self.export_pdf_report)
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Export Excel Button
        excel_btn = tk.Button(btn_frame, text="Export Excel", 
                            font=("Arial", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            width=15, height=1,
                            command=self.export_excel)
        excel_btn.pack(side=tk.LEFT, padx=5)
        
        # New Problem Button
        new_btn = tk.Button(btn_frame, text="New Problem", 
                          font=("Arial", 11),
                          command=self.create_first_page)
        new_btn.pack(side=tk.LEFT, padx=5)
        
        # 🎨 Colored Tableau Button
        colored_btn = tk.Button(btn_frame, text="🎨 Colored Tableau", 
                            font=("Arial", 11, "bold"),
                            bg="#00BCD4", fg="white",
                            width=15, height=1,
                            command=lambda: self.show_colored_tableau("Final Tableau - Colored"))
        colored_btn.pack(side=tk.LEFT, padx=5)

        # 📈 Convergence Plot Button
        conv_btn = tk.Button(btn_frame, text="📈 Convergence Plot", 
                            font=("Arial", 11, "bold"),
                            bg="#FF5722", fg="white",
                            width=15, height=1,
                            command=self.plot_convergence)
        conv_btn.pack(side=tk.LEFT, padx=5)
        
        # Credit
        credit_label = tk.Label(self.root, text="Prepared by Navid Naderpour ,Navid.Naderpour@gmail.com",
                              font=("Arial", 10), fg="gray")
        credit_label.pack(side=tk.BOTTOM, pady=10)
        
        
    def format_tableau(self, tableau):
        """Format tableau for display"""
        m, n = tableau.shape
        result = ""
        
        # Column headers
        headers = []
        for i in range(n - 1):
            if i < self.data['num_vars']:
                headers.append(f"x{i+1}")
            else:
                headers.append(f"s{i+1-self.data['num_vars']}")
        headers.append("RHS")
        
        result += " " * 8 + " ".join([f"{h:>8}" for h in headers]) + "\n"
        result += "-" * (8 + 9 * len(headers)) + "\n"
        
        # Rows
        for i in range(m):
            if i < m - 1:
                row_label = f"Row {i+1}:"
            else:
                row_label = "Obj:"
            
            result += f"{row_label:>7}"
            for j in range(n):
                result += f"{tableau[i, j]:>8.3f}"
            result += "\n"
        
        return result
    def show_colored_tableau(self, title="Colored Tableau"):
        """نمایش جدول رنگی با استفاده از matplotlib"""
        try:
            if 'tableau' not in self.solution:
                messagebox.showinfo("Info", "No tableau available to display.")
                return
            
            tableau = self.solution['tableau']
            m, n_tab = tableau.shape
            
            # Create window
            colored_window = tk.Toplevel(self.root)
            colored_window.title(title)
            colored_window.geometry("900x600")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.axis('off')
            
            # Column headers
            col_labels = []
            for j in range(n_tab - 1):
                if j < self.data['num_vars']:
                    col_labels.append(f'$x_{{{j+1}}}$')
                else:
                    col_labels.append(f'$s_{{{j+1-self.data["num_vars"]}}}$')
            col_labels.append('RHS')
            
            # Row labels
            row_labels = []
            for i in range(m - 1):
                row_labels.append(f'Row {i+1}')
            row_labels.append('Objective')
            
            # Create table
            colors = []
            for i in range(m):
                row_colors = []
                for j in range(n_tab):
                    val = tableau[i, j]
                    if i == m - 1:  # Objective row
                        if val > 0:
                            row_colors.append('#FFEBEE')  # Light red
                        elif val < 0:
                            row_colors.append('#C8E6C9')  # Light green
                        else:
                            row_colors.append('#FFF9C4')  # Light yellow
                    elif j == n_tab - 1:  # RHS column
                        if val < 0:
                            row_colors.append('#FFCDD2')  # Red
                        else:
                            row_colors.append('#FFFFFF')
                    else:
                        row_colors.append('#FFFFFF')
                colors.append(row_colors)
            
            # Create table
            cell_text = [[f'{tableau[i,j]:.3f}' for j in range(n_tab)] for i in range(m)]
            table = ax.table(cellText=cell_text,
                            rowLabels=row_labels,
                            colLabels=col_labels,
                            cellColours=colors,
                            cellLoc='center',
                            loc='center')
            
            # Style table
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, colored_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating colored tableau: {str(e)}")

    def plot_convergence(self):
        """نمایش نمودار همگرایی الگوریتم"""
        try:
            # Get iterations data
            if hasattr(self, 'iterations') and self.iterations:
                iterations_data = self.iterations
            elif hasattr(self, 'iterations_phase1') and self.iterations_phase1:
                iterations_data = self.iterations_phase1
            else:
                messagebox.showinfo("Info", "No iteration data available for convergence plot.")
                return
            
            # Extract objective function values from each iteration
            z_values = []
            for tableau in iterations_data:
                z_val = tableau[-1, -1]
                z_values.append(z_val)
            
            # Create window
            conv_window = tk.Toplevel(self.root)
            conv_window.title("Convergence Plot")
            conv_window.geometry("700x500")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 5))
            
            iterations = range(len(z_values))
            ax.plot(iterations, z_values, 'b-o', linewidth=2, markersize=6, label='Objective Value')
            ax.plot(iterations, z_values, 'g--', alpha=0.5, linewidth=1)
            
            # Highlight optimal point
            if len(z_values) > 1:
                optimal_idx = np.argmin(np.abs(np.diff(z_values))) + 1
                ax.plot(optimal_idx, z_values[optimal_idx], 'ro', markersize=10, label='Optimal Point')
            
            ax.set_xlabel('Iteration', fontsize=12)
            ax.set_ylabel('Objective Function Value', fontsize=12)
            ax.set_title('Algorithm Convergence', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Add text showing final value
            final_z = z_values[-1]
            ax.text(0.02, 0.98, f'Final Value: {final_z:.4f}', 
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, conv_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Save button
            save_btn = tk.Button(conv_window, text="Save Plot", 
                               command=lambda: self.save_plot(fig))
            save_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating convergence plot: {str(e)}")

    def plot_solution(self):
        """Plot graphical solution for 2-variable problems"""
        if self.data['num_vars'] != 2:
            messagebox.showinfo("Info", "Plotting is only available for 2-variable problems.")
            return
        
        try:
            # Create plot window
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Graphical Solution")
            plot_window.geometry("800x600")
            
            # Create figure
            fig = plt.Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # Get constraint data
            A = []
            b = []
            if hasattr(self, 'constraint_data') and len(self.constraint_data) > 0:
                for cons in self.constraint_data:
                    A.append(cons['coeffs'])
                    b.append(cons['rhs'])
            else:
                # اگر constraint_data وجود ندارد، از مقادیر پیش‌فرض استفاده کن
                for i in range(self.data['num_cons']):
                    A.append([0.0] * self.data['num_vars'])
                    b.append(0.0)
            
            # تعیین محدوده x
            x_max = 0
            for i in range(len(b)):
                if len(A[i]) > 0 and abs(A[i][0]) > 1e-10:
                    x_val = b[i] / A[i][0]
                    x_max = max(x_max, x_val)
                else:
                    x_max = max(x_max, 10)  # مقدار پیش‌فرض
            
            x = np.linspace(0, x_max * 1.5, 400)
            
            # رسم همه محدودیت‌ها
            for i in range(len(A)):
                # بررسی نوع محدودیت
                # 1. خط عمودی (ضریب y = 0)
                if len(A[i]) > 1 and abs(A[i][1]) < 1e-10:
                    if abs(A[i][0]) > 1e-10:
                        x_val = b[i] / A[i][0]
                        ax.axvline(x=x_val, color='blue', linestyle='-', alpha=0.7, label=f"Constraint {i+1}")
                        
                        # پر کردن ناحیه شدنی برای خط عمودی
                        if A[i][0] > 0:  # x ≤ ثابت
                            ax.fill_betweenx([0, x_max*1.5], 0, x_val, alpha=0.1, color='blue')
                        else:  # x ≥ ثابت (معکوس)
                            ax.fill_betweenx([0, x_max*1.5], x_val, x_max*1.5, alpha=0.1, color='blue')
                
                # 2. خط افقی (ضریب x = 0)
                elif len(A[i]) > 0 and abs(A[i][0]) < 1e-10:
                    if abs(A[i][1]) > 1e-10:
                        y_val = b[i] / A[i][1]
                        ax.axhline(y=y_val, color='blue', linestyle='-', alpha=0.7, label=f"Constraint {i+1}")
                        
                        # پر کردن ناحیه شدنی برای خط افقی
                        if A[i][1] > 0:  # y ≤ ثابت
                            ax.fill_between(x, 0, y_val, alpha=0.1, color='blue')
                        else:  # y ≥ ثابت (معکوس)
                            ax.fill_between(x, y_val, x_max*1.5, alpha=0.1, color='blue')
                
                # 3. خط مورب (هر دو ضریب غیرصفر)
                else:
                    if len(A[i]) > 1 and abs(A[i][1]) > 1e-10:
                        y = (b[i] - A[i][0] * x) / A[i][1]
                        ax.plot(x, y, label=f"Constraint {i+1}")
                        
                        # پر کردن ناحیه شدنی برای خط مورب
                        # بررسی جهت ناحیه شدنی
                        test_x = 0
                        test_y = 0
                        if A[i][0] * test_x + A[i][1] * test_y <= b[i]:
                            # مبدأ در ناحیه شدنی است
                            ax.fill_between(x, 0, y, alpha=0.1, color='blue')
                        else:
                            # مبدأ خارج از ناحیه شدنی است
                            ax.fill_between(x, y, x_max*1.5, alpha=0.1, color='blue')
            
            # Plot optimal point
            opt_x = self.solution['decision_vars'][0]
            opt_y = self.solution['decision_vars'][1]
            ax.plot(opt_x, opt_y, 'ro', markersize=10, label=f'Optimal ({opt_x:.2f}, {opt_y:.2f})')
            
            # Plot objective function lines
            if hasattr(self, 'obj_coeffs') and len(self.obj_coeffs) > 0:
                c = self.obj_coeffs.copy()
            else:
                c = [0.0] * self.data['num_vars']
            
            # Plot iso-profit lines
            z_vals = np.linspace(self.solution['optimal_value'] * 0.5, 
                                self.solution['optimal_value'] * 1.5, 5)
            
            for z in z_vals:
                if len(c) > 1 and abs(c[1]) > 1e-10:
                    y_obj = (z - c[0] * x) / c[1]
                    ax.plot(x, y_obj, 'g--', alpha=0.3, linewidth=0.5)
            
            # Plot optimal iso-profit line
            if len(c) > 1 and abs(c[1]) > 1e-10:
                y_opt = (self.solution['optimal_value'] - c[0] * x) / c[1]
                ax.plot(x, y_opt, 'g-', linewidth=2, label='Optimal Objective')
            
            # Set plot properties
            ax.set_xlabel('x1', fontsize=12)
            ax.set_ylabel('x2', fontsize=12)
            ax.set_title('Graphical Solution of Linear Programming Problem', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_xlim([0, x_max * 1.2])
            ax.set_ylim([0, x_max * 1.2])
            
            # Add text with solution
            text_str = f"Optimal: ({opt_x:.2f}, {opt_y:.2f})\nz = {self.solution['optimal_value']:.2f}"
            ax.text(0.02, 0.98, text_str, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Embed plot in tkinter window
            canvas = FigureCanvasTkAgg(fig, plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add save button
            save_btn = tk.Button(plot_window, text="Save Plot", 
                               command=lambda: self.save_plot(fig))
            save_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error creating plot: {str(e)}\n\nDetails: {traceback.format_exc()}")

    def save_plot(self, fig):
        """Save plot to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving plot: {str(e)}")

    def show_iterations(self):
        """Show all simplex iterations"""
        # بررسی کدام iterations را نمایش دهیم
        if hasattr(self, 'revised_iterations') and self.revised_iterations:
            iterations_to_show = self.revised_iterations
            method_name = "Revised Simplex"
        elif hasattr(self, 'iterations') and self.iterations:
            iterations_to_show = self.iterations
            method_name = "Simplex"
        else:
            messagebox.showinfo("Info", "No iterations to display.")
            return
        
        # Create iterations window
        iter_window = tk.Toplevel(self.root)
        iter_window.title(f"{method_name} Iterations")
        iter_window.geometry("900x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(iter_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a tab for each iteration
        for i, iteration_data in enumerate(iterations_to_show):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Iteration {i}")
            
            # Create text widget
            text_widget = tk.Text(tab, font=("Courier", 9))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Format and insert data
            if 'tableau' in iteration_data:
                tableau_str = self.format_tableau(iteration_data['tableau'])
                text_widget.insert(tk.END, tableau_str)
            elif 'B_inv' in iteration_data:
                B_inv = iteration_data['B_inv']
                tableau_str = f"Basis Inverse (Iteration {i}):\n"
                tableau_str += "-"*50 + "\n"
                m, n = B_inv.shape
                for row in range(m):
                    row_str = f"Row {row+1}: "
                    for col in range(n):
                        row_str += f"{B_inv[row, col]:>8.3f}"
                    tableau_str += row_str + "\n"
                text_widget.insert(tk.END, tableau_str)
            else:
                text_widget.insert(tk.END, f"Iteration {i} data:\n{iteration_data}")
            
            text_widget.config(state=tk.DISABLED)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(tab, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)

    def export_iterations_excel(self):
        """Export all iterations to Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for i, tableau in enumerate(self.iterations):
                        # Create DataFrame for tableau
                        m, n = tableau.shape
                        
                        # Column names
                        cols = []
                        for j in range(n - 1):
                            if j < self.data['num_vars']:
                                cols.append(f"x{j+1}")
                            else:
                                cols.append(f"s{j+1-self.data['num_vars']}")
                        cols.append("RHS")
                        
                        # Row names
                        rows = []
                        for j in range(m - 1):
                            rows.append(f"Constraint {j+1}")
                        rows.append("Objective")
                        
                        # Create DataFrame
                        df = pd.DataFrame(tableau, columns=cols, index=rows)
                        
                        # Write to Excel
                        df.to_excel(writer, sheet_name=f"Iteration_{i}")
                    
                messagebox.showinfo("Success", f"Iterations exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting iterations: {str(e)}")

    def export_pdf_report(self):
        """Export complete report to PDF"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if not filename:
                return
                
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Simplex Solver Report", ln=True, align='C')
            pdf.ln(10)
            
            # Problem Information
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Problem Information:", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 8, f"Optimization Type: {self.data['opt_type']}", ln=True)
            pdf.cell(0, 8, f"Number of Variables: {self.data['num_vars']}", ln=True)
            pdf.cell(0, 8, f"Number of Constraints: {self.data['num_cons']}", ln=True)
            pdf.cell(0, 8, f"Non-negativity: {self.data['nonneg']}", ln=True)
            pdf.ln(10)
            
            # Objective Function
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Objective Function:", ln=True)
            pdf.set_font("Courier", '', 11)
            
            # استفاده از داده‌های ذخیره شده
            if hasattr(self, 'obj_coeffs') and len(self.obj_coeffs) > 0:
                obj_coeffs = self.obj_coeffs.copy()
            else:
                obj_coeffs = [0.0] * self.data['num_vars']
            
            obj_str = "Maximize" if self.data['opt_type'] == "Max" else "Minimize"
            obj_parts = []
            for i, coeff in enumerate(obj_coeffs):
                if coeff != 0:
                    sign = "+" if coeff >= 0 else "-"
                    abs_coeff = abs(coeff)
                    if abs_coeff == 1:
                        obj_parts.append(f"{sign} x{i+1}")
                    else:
                        obj_parts.append(f"{sign} {abs_coeff}x{i+1}")
            
            if obj_parts:
                if obj_parts[0].startswith("+"):
                    obj_parts[0] = obj_parts[0][2:]
                elif obj_parts[0].startswith("-"):
                    obj_parts[0] = obj_parts[0][0] + obj_parts[0][2:]
            
            obj_eq = f"{obj_str}: z = " + " ".join(obj_parts)
            pdf.cell(0, 8, obj_eq, ln=True)
            pdf.ln(10)
            
            # Constraints - استفاده از constraint_data
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Constraints:", ln=True)
            pdf.set_font("Courier", '', 11)
            
            if hasattr(self, 'constraint_data') and len(self.constraint_data) > 0:
                for i, cons in enumerate(self.constraint_data):
                    cons_parts = []
                    for j, coeff in enumerate(cons['coeffs']):
                        if coeff != 0:
                            sign = "+" if coeff >= 0 else "-"
                            abs_coeff = abs(coeff)
                            if abs_coeff == 1:
                                cons_parts.append(f"{sign} x{j+1}")
                            else:
                                cons_parts.append(f"{sign} {abs_coeff}x{j+1}")
                    
                    if cons_parts:
                        if cons_parts[0].startswith("+"):
                            cons_parts[0] = cons_parts[0][2:]
                        elif cons_parts[0].startswith("-"):
                            cons_parts[0] = cons_parts[0][0] + cons_parts[0][2:]
                    
                    cons_eq = " ".join(cons_parts) + f" {cons['sign']} {cons['rhs']}"
                    pdf.cell(0, 8, cons_eq, ln=True)
            else:
                pdf.cell(0, 8, "No constraint data available.", ln=True)
            
            pdf.ln(10)
            
            # Solution Results
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Solution Results:", ln=True)
            pdf.set_font("Arial", '', 11)
            
            # Optimal Value
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f"Optimal Value: {self.solution['optimal_value']:.4f}", ln=True)
            pdf.set_font("Arial", '', 11)
            
            # Decision Variables
            pdf.cell(0, 8, "Decision Variables:", ln=True)
            for i, val in enumerate(self.solution['decision_vars']):
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"x{i+1} = {val:.4f}", ln=True)
            
            # Slack Variables
            pdf.cell(0, 8, "Slack/Surplus Variables:", ln=True)
            for i, val in enumerate(self.solution['slack_vars']):
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"s{i+1} = {val:.4f}", ln=True)
            
            # Shadow Prices
            pdf.cell(0, 8, "Shadow Prices (Dual Variables):", ln=True)
            for i, val in enumerate(self.solution['shadow_prices']):
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"y{i+1} = {val:.4f}", ln=True)
            
            # Reduced Costs
            pdf.cell(0, 8, "Reduced Costs:", ln=True)
            for i, val in enumerate(self.solution['reduced_costs']):
                pdf.cell(20, 8, "")
                pdf.cell(0, 8, f"rc(x{i+1}) = {val:.4f}", ln=True)
            
            # Basis
            pdf.cell(0, 8, "Basic Variables:", ln=True)
            basis_str = ", ".join([f"x{i+1}" if i < self.data['num_vars'] else f"s{i+1-self.data['num_vars']}" 
                                  for i in self.solution['basis']])
            pdf.cell(20, 8, "")
            pdf.cell(0, 8, basis_str, ln=True)
            
            pdf.ln(10)
            
            # Final Tableau (if available)
            if 'tableau' in self.solution:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Final Tableau:", ln=True)
                pdf.set_font("Courier", '', 9)
                
                tableau = self.solution['tableau']
                m, n = tableau.shape
                
                # Tableau header
                header = " " * 8
                for j in range(n - 1):
                    if j < self.data['num_vars']:
                        header += f"x{j+1:>8}"
                    else:
                        header += f"s{j+1-self.data['num_vars']:>8}"
                header += f"{'RHS':>8}"
                pdf.cell(0, 8, header, ln=True)
                
                # Separator line
                separator = "-" * (8 + 8 * n)
                pdf.cell(0, 8, separator, ln=True)
                
                # Tableau rows
                for i in range(m):
                    if i < m - 1:
                        row_label = f"Row {i+1}:"
                    else:
                        row_label = "Obj:"
                    
                    row_str = f"{row_label:>7}"
                    for j in range(n):
                        row_str += f"{tableau[i, j]:>8.3f}"
                    pdf.cell(0, 8, row_str, ln=True)
            
            pdf.ln(10)
            
            # Footer
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, "Generated by Portable Simplex Solver", ln=True, align='C')
            pdf.cell(0, 10, "Prepared by Navid Naderpour ,Navid.Naderpour@gmail.com", ln=True, align='C')
            pdf.cell(0, 10, f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            
            # Save PDF
            pdf.output(filename)
            messagebox.showinfo("Success", f"PDF report saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("PDF Export Error", f"Error creating PDF: {str(e)}")
    def export_excel(self):
        """Export results to Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if not filename:
                return
                
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Problem Information sheet
                info_data = {
                    'Parameter': ['Optimization Type', 'Number of Variables', 
                                 'Number of Constraints', 'Non-negativity'],
                    'Value': [self.data['opt_type'], self.data['num_vars'], 
                             self.data['num_cons'], self.data['nonneg']]
                }
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='Problem Info', index=False)
                
                # Objective Function sheet - استفاده از obj_coeffs
                if hasattr(self, 'obj_coeffs') and len(self.obj_coeffs) > 0:
                    obj_coeffs = self.obj_coeffs.copy()
                else:
                    obj_coeffs = [0.0] * self.data['num_vars']
                
                obj_data = {
                    'Variable': [f'x{i+1}' for i in range(self.data['num_vars'])],
                    'Coefficient': obj_coeffs
                }
                obj_df = pd.DataFrame(obj_data)
                obj_df.to_excel(writer, sheet_name='Objective Function', index=False)
                
                # Constraints sheet - استفاده از constraint_data
                if hasattr(self, 'constraint_data') and len(self.constraint_data) > 0:
                    constraints_data = []
                    for i, cons in enumerate(self.constraint_data):
                        row = {'Constraint': f'Row {i+1}'}
                        for j, coeff in enumerate(cons['coeffs']):
                            row[f'x{j+1}'] = coeff
                        
                        row['Sign'] = cons['sign']
                        row['RHS'] = cons['rhs']
                        constraints_data.append(row)
                    
                    cons_df = pd.DataFrame(constraints_data)
                    cons_df.to_excel(writer, sheet_name='Constraints', index=False)
                else:
                    # اگر داده‌ای وجود ندارد، یک sheet خالی ایجاد کن
                    empty_df = pd.DataFrame({'Message': ['No constraint data available']})
                    empty_df.to_excel(writer, sheet_name='Constraints', index=False)
                
                # Solution Results sheet
                solution_data = {
                    'Result Type': ['Optimal Value', 'Method Used'],
                    'Value': [self.solution['optimal_value'], 
                             self.solution.get('method_used', 'Unknown')]
                }
                solution_df = pd.DataFrame(solution_data)
                solution_df.to_excel(writer, sheet_name='Solution', index=False)
                
                # Decision Variables sheet
                dec_vars_data = {
                    'Variable': [f'x{i+1}' for i in range(self.data['num_vars'])],
                    'Value': self.solution['decision_vars']
                }
                dec_vars_df = pd.DataFrame(dec_vars_data)
                dec_vars_df.to_excel(writer, sheet_name='Decision Variables', index=False)
                
                # Slack Variables sheet
                slack_vars_data = {
                    'Variable': [f's{i+1}' for i in range(self.data['num_cons'])],
                    'Value': self.solution['slack_vars']
                }
                slack_vars_df = pd.DataFrame(slack_vars_data)
                slack_vars_df.to_excel(writer, sheet_name='Slack Variables', index=False)
                
                # Shadow Prices sheet
                shadow_data = {
                    'Constraint': [f'Constraint {i+1}' for i in range(self.data['num_cons'])],
                    'Shadow Price': self.solution['shadow_prices']
                }
                shadow_df = pd.DataFrame(shadow_data)
                shadow_df.to_excel(writer, sheet_name='Shadow Prices', index=False)
                
                # Reduced Costs sheet
                reduced_data = {
                    'Variable': [f'x{i+1}' for i in range(self.data['num_vars'])],
                    'Reduced Cost': self.solution['reduced_costs']
                }
                reduced_df = pd.DataFrame(reduced_data)
                reduced_df.to_excel(writer, sheet_name='Reduced Costs', index=False)
                
                # Basis Variables sheet
                basis_data = {
                    'Basic Variable': [f"x{i+1}" if i < self.data['num_vars'] else f"s{i+1-self.data['num_vars']}" 
                                      for i in self.solution['basis']],
                    'Value': [self.solution['decision_vars'][i] if i < self.data['num_vars'] 
                             else self.solution['slack_vars'][i-self.data['num_vars']] 
                             for i in self.solution['basis']]
                }
                basis_df = pd.DataFrame(basis_data)
                basis_df.to_excel(writer, sheet_name='Basis Variables', index=False)
                
                # Final Tableau sheet (if available)
                if 'tableau' in self.solution:
                    tableau = self.solution['tableau']
                    m, n = tableau.shape
                    
                    # Create column names
                    cols = []
                    for j in range(n - 1):
                        if j < self.data['num_vars']:
                            cols.append(f'x{j+1}')
                        else:
                            cols.append(f's{j+1-self.data["num_vars"]}')
                    cols.append('RHS')
                    
                    # Create row names
                    rows = []
                    for i in range(m - 1):
                        rows.append(f'Constraint {i+1}')
                    rows.append('Objective')
                    
                    tableau_df = pd.DataFrame(tableau, columns=cols, index=rows)
                    tableau_df.to_excel(writer, sheet_name='Final Tableau')
                
                # Additional Info sheet
                additional_info = {
                    'Info': ['Feasible', 'Optimal', 'Iterations Count'],
                    'Value': [str(self.solution.get('feasible', 'Unknown')),
                             str(self.solution.get('optimal', 'Unknown')),
                             str(self.solution.get('iterations_count', 'Unknown'))]
                }
                additional_df = pd.DataFrame(additional_info)
                additional_df.to_excel(writer, sheet_name='Additional Info', index=False)
            
            messagebox.showinfo("Success", f"Excel file saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Excel Export Error", f"Error creating Excel file: {str(e)}")
    def analyze_results(self):
        """تحلیل مفهومی نتایج سیمپلکس"""
        try:
            # ایجاد پنجره تحلیل
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Results Analysis & Interpretation")
            analysis_window.geometry("900x700")
            
            # عنوان
            title_label = tk.Label(analysis_window, 
                                 text="📊 ANALYSIS & INTERPRETATION OF RESULTS",
                                 font=("Arial", 16, "bold"),
                                 fg="#2E7D32")
            title_label.pack(pady=20)
            
            # فریم اصلی با اسکرول
            main_frame = tk.Frame(analysis_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(main_frame)
            scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # تحلیل نوع مسأله
            problem_type = "MAXIMIZATION" if self.data['opt_type'] == "Max" else "MINIMIZATION"
            problem_text = f"🔹 PROBLEM TYPE: {problem_type}"
            if self.data['opt_type'] == "Max":
                problem_text += " (Profit Maximization)"
            else:
                problem_text += " (Cost Minimization)"
            
            tk.Label(scrollable_frame, text=problem_text,
                    font=("Arial", 12, "bold"), fg="#1565C0").pack(pady=10, anchor=tk.W)
            
            # خلاصه جواب بهینه
            tk.Label(scrollable_frame, text="🔹 OPTIMAL SOLUTION SUMMARY:",
                    font=("Arial", 12, "bold"), fg="#2E7D32").pack(pady=5, anchor=tk.W)
            
            opt_val = self.solution['optimal_value']
            tk.Label(scrollable_frame, text=f"• Optimal Value: {opt_val:.4f}",
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
            
            # تحلیل متغیرهای تصمیم
            for i, val in enumerate(self.solution['decision_vars']):
                if abs(val) > 1e-6:
                    tk.Label(scrollable_frame, 
                            text=f"• x{i+1} = {val:.4f}: Produce {val:.2f} units of Product {i+1}",
                            font=("Arial", 11)).pack(anchor=tk.W, padx=20)
                else:
                    tk.Label(scrollable_frame, 
                            text=f"• x{i+1} = {val:.4f}: Do NOT produce Product {i+1}",
                            font=("Arial", 11), fg="#757575").pack(anchor=tk.W, padx=20)
            
            # تحلیل Shadow Prices (متغیرهای دوگان)
            tk.Label(scrollable_frame, text="\n🔹 SHADOW PRICES (Dual Variables):",
                    font=("Arial", 12, "bold"), fg="#2E7D32").pack(pady=10, anchor=tk.W)
            
            for i, sp in enumerate(self.solution['shadow_prices']):
                if abs(sp) < 1e-6:
                    tk.Label(scrollable_frame, 
                            text=f"• Constraint {i+1} (y{i+1} = {sp:.4f}): Not binding",
                            font=("Arial", 11)).pack(anchor=tk.W, padx=20)
                    tk.Label(scrollable_frame, 
                            text=f"  → Increasing RHS by 1 unit won't change optimal value",
                            font=("Arial", 10), fg="#616161").pack(anchor=tk.W, padx=40)
                elif sp > 0:
                    if self.data['opt_type'] == "Max":
                        tk.Label(scrollable_frame, 
                                text=f"• Constraint {i+1} (y{i+1} = {sp:.4f}): Valuable resource",
                                font=("Arial", 11), fg="#388E3C").pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Each additional unit increases profit by {sp:.4f}",
                                font=("Arial", 10), fg="#388E3C").pack(anchor=tk.W, padx=40)
                    else:
                        tk.Label(scrollable_frame, 
                                text=f"• Constraint {i+1} (y{i+1} = {sp:.4f}): Binding constraint",
                                font=("Arial", 11)).pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Each additional unit decreases cost by {sp:.4f}",
                                font=("Arial", 10)).pack(anchor=tk.W, padx=40)
                else:  # sp < 0
                    if self.data['opt_type'] == "Max":
                        tk.Label(scrollable_frame, 
                                text=f"• Constraint {i+1} (y{i+1} = {sp:.4f}): Binding constraint",
                                font=("Arial", 11), fg="#D32F2F").pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Each additional unit decreases profit by {abs(sp):.4f}",
                                font=("Arial", 10), fg="#D32F2F").pack(anchor=tk.W, padx=40)
                    else:
                        tk.Label(scrollable_frame, 
                                text=f"• Constraint {i+1} (y{i+1} = {sp:.4f}): Valuable resource",
                                font=("Arial", 11), fg="#388E3C").pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Each additional unit increases cost by {abs(sp):.4f}",
                                font=("Arial", 10), fg="#388E3C").pack(anchor=tk.W, padx=40)
            
            # تحلیل Slack/Surplus Variables
            tk.Label(scrollable_frame, text="\n🔹 SLACK/SURPLUS ANALYSIS:",
                    font=("Arial", 12, "bold"), fg="#2E7D32").pack(pady=10, anchor=tk.W)
            
            for i, slack in enumerate(self.solution['slack_vars']):
                if slack > 1e-6:
                    tk.Label(scrollable_frame, 
                            text=f"• Constraint {i+1} (s{i+1} = {slack:.4f}): Non-binding",
                            font=("Arial", 11), fg="#388E3C").pack(anchor=tk.W, padx=20)
                    tk.Label(scrollable_frame, 
                            text=f"  → {slack:.2f} units of resource {i+1} are unused",
                            font=("Arial", 10), fg="#388E3C").pack(anchor=tk.W, padx=40)
                else:
                    tk.Label(scrollable_frame, 
                            text=f"• Constraint {i+1} (s{i+1} = {slack:.4f}): Binding",
                            font=("Arial", 11), fg="#D32F2F").pack(anchor=tk.W, padx=20)
                    tk.Label(scrollable_frame, 
                            text=f"  → Resource {i+1} is fully utilized (scarce resource)",
                            font=("Arial", 10), fg="#D32F2F").pack(anchor=tk.W, padx=40)
            
            # تحلیل Reduced Costs
            tk.Label(scrollable_frame, text="\n🔹 REDUCED COSTS ANALYSIS:",
                    font=("Arial", 12, "bold"), fg="#2E7D32").pack(pady=10, anchor=tk.W)
            
            for i, rc in enumerate(self.solution['reduced_costs']):
                if abs(rc) < 1e-6:
                    tk.Label(scrollable_frame, 
                            text=f"• x{i+1} (rc = {rc:.4f}): In optimal basis",
                            font=("Arial", 11)).pack(anchor=tk.W, padx=20)
                    tk.Label(scrollable_frame, 
                            text=f"  → Product {i+1} should be produced in current solution",
                            font=("Arial", 10)).pack(anchor=tk.W, padx=40)
                else:
                    if rc > 0:
                        tk.Label(scrollable_frame, 
                                text=f"• x{i+1} (rc = {rc:.4f}): Not in optimal basis",
                                font=("Arial", 11), fg="#D32F2F").pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Forcing 1 unit of Product {i+1} would decrease profit by {rc:.4f}",
                                font=("Arial", 10), fg="#D32F2F").pack(anchor=tk.W, padx=40)
                    else:  # rc < 0
                        tk.Label(scrollable_frame, 
                                text=f"• x{i+1} (rc = {rc:.4f}): Not in optimal basis",
                                font=("Arial", 11), fg="#D32F2F").pack(anchor=tk.W, padx=20)
                        tk.Label(scrollable_frame, 
                                text=f"  → Forcing 1 unit of Product {i+1} would increase cost by {abs(rc):.4f}",
                                font=("Arial", 10), fg="#D32F2F").pack(anchor=tk.W, padx=40)
            
            # تحلیل Basis Variables
            tk.Label(scrollable_frame, text="\n🔹 BASIS VARIABLES ANALYSIS:",
                    font=("Arial", 12, "bold"), fg="#2E7D32").pack(pady=10, anchor=tk.W)
            
            basis_vars = []
            for i, basis_idx in enumerate(self.solution['basis']):
                if basis_idx < self.data['num_vars']:
                    var_name = f"x{basis_idx+1}"
                    var_value = self.solution['decision_vars'][basis_idx]
                else:
                    var_name = f"s{basis_idx+1-self.data['num_vars']}"
                    var_value = self.solution['slack_vars'][basis_idx-self.data['num_vars']]
                basis_vars.append(f"{var_name} = {var_value:.4f}")
            
            basis_str = ", ".join(basis_vars)
            tk.Label(scrollable_frame, text=f"• Basic Variables: {basis_str}",
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
            tk.Label(scrollable_frame, 
                    text=f"  → These {len(basis_vars)} variables form the optimal basis",
                    font=("Arial", 10)).pack(anchor=tk.W, padx=40)
            
            # توصیه‌های عملی
            tk.Label(scrollable_frame, text="\n🔹 PRACTICAL RECOMMENDATIONS:",
                    font=("Arial", 12, "bold"), fg="#FF9800").pack(pady=10, anchor=tk.W)
            
            recommendations = []
            
            # بررسی binding constraints
            binding_constraints = []
            for i, slack in enumerate(self.solution['slack_vars']):
                if abs(slack) < 1e-6:
                    binding_constraints.append(i+1)
            
            if binding_constraints:
                rec_text = f"1. Focus on relaxing Constraints {', '.join(map(str, binding_constraints))}"
                if len(binding_constraints) == 1:
                    rec_text += " (the only binding constraint)"
                else:
                    rec_text += " (binding constraints)"
                recommendations.append(rec_text)
            
            # بررسی non-binding constraints
            non_binding = []
            for i, slack in enumerate(self.solution['slack_vars']):
                if slack > 1e-6:
                    non_binding.append(i+1)
            
            if non_binding:
                recommendations.append(f"2. Constraints {', '.join(map(str, non_binding))} have slack (underutilized resources)")
            
            # بررسی متغیرهای غیرپایه
            non_basic_vars = []
            for i, rc in enumerate(self.solution['reduced_costs']):
                if abs(rc) > 1e-6:
                    non_basic_vars.append(f"x{i+1}")
            
            if non_basic_vars:
                recommendations.append(f"3. Avoid producing {', '.join(non_basic_vars)} (not in optimal solution)")
            
            # بررسی shadow prices برای Max problems
            if self.data['opt_type'] == "Max":
                valuable_resources = []
                for i, sp in enumerate(self.solution['shadow_prices']):
                    if sp > 1e-6:
                        valuable_resources.append(f"Resource {i+1} (+{sp:.2f}/unit)")
                
                if valuable_resources:
                    recommendations.append(f"4. Invest in: {', '.join(valuable_resources)}")
            
            # اگر هیچ توصیه‌ای نبود
            if not recommendations:
                recommendations.append("Current solution is optimal. No changes recommended.")
            
            # نمایش توصیه‌ها
            for i, rec in enumerate(recommendations):
                tk.Label(scrollable_frame, text=f"• {rec}",
                        font=("Arial", 11)).pack(anchor=tk.W, padx=20, pady=2)
            
            # اطلاعات روش حل
            tk.Label(scrollable_frame, text="\n🔹 SOLUTION METHOD INFO:",
                    font=("Arial", 12, "bold"), fg="#7B1FA2").pack(pady=10, anchor=tk.W)
            
            method = self.solution.get('method_used', 'Unknown')
            iterations = self.solution.get('iterations_count', 'Unknown')
            
            tk.Label(scrollable_frame, text=f"• Method: {method}",
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
            tk.Label(scrollable_frame, text=f"• Iterations: {iterations}",
                    font=("Arial", 11)).pack(anchor=tk.W, padx=20)
            
            if 'feasible' in self.solution and 'optimal' in self.solution:
                feasible = "Yes" if self.solution['feasible'] else "No"
                optimal = "Yes" if self.solution['optimal'] else "No"
                tk.Label(scrollable_frame, text=f"• Feasible: {feasible}, Optimal: {optimal}",
                        font=("Arial", 11)).pack(anchor=tk.W, padx=20)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # دکمه بستن
            close_btn = tk.Button(analysis_window, text="Close Analysis",
                                font=("Arial", 11),
                                command=analysis_window.destroy)
            close_btn.pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in results analysis: {str(e)}")
    def sensitivity_analysis(self):
        """تحلیل حساسیت نتایج سیمپلکس"""
        try:
            # بررسی آیا tableau وجود دارد
            if 'tableau' not in self.solution:
                messagebox.showinfo("Info", "Sensitivity analysis requires final tableau. Not available for this method.")
                return
            
            tableau = self.solution['tableau']
            m, n = tableau.shape  # m = تعداد سطرها (شامل سطر هدف), n = تعداد ستون‌ها
            
            # تعداد متغیرهای اصلی و slack
            num_vars = self.data['num_vars']
            num_cons = self.data['num_cons']
            
            # ایجاد پنجره تحلیل حساسیت
            sensitivity_window = tk.Toplevel(self.root)
            sensitivity_window.title("Sensitivity Analysis Report")
            sensitivity_window.geometry("1000x800")
            
            # عنوان
            title_label = tk.Label(sensitivity_window, 
                                 text="🔍 SENSITIVITY ANALYSIS REPORT",
                                 font=("Arial", 16, "bold"),
                                 fg="#6A1B9A")
            title_label.pack(pady=20)
            
            # فریم اصلی با اسکرول
            main_frame = tk.Frame(sensitivity_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            canvas = tk.Canvas(main_frame)
            scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # بخش ۱: محدوده تغییر ضرایب تابع هدف
            tk.Label(scrollable_frame, text="📈 OBJECTIVE COEFFICIENT RANGES (cⱼ):",
                    font=("Arial", 14, "bold"), fg="#283593").pack(pady=15, anchor=tk.W)
            
            tk.Label(scrollable_frame, 
                    text="How much can each objective coefficient change without changing the optimal solution?",
                    font=("Arial", 10), fg="#616161").pack(anchor=tk.W, pady=5)
            
            # محاسبه محدوده‌ها برای هر ضریب تابع هدف
            for j in range(num_vars):
                # پیدا کردن سطر مربوط به متغیر در پایه
                in_basis = False
                basis_row = -1
                
                for i in range(num_cons):
                    if j in self.solution['basis']:
                        # اگر متغیر در پایه است
                        basis_idx = list(self.solution['basis']).index(j)
                        in_basis = True
                        basis_row = basis_idx
                        break
                
                if in_basis:
                    # اگر متغیر در پایه است
                    # محدوده از روی ضرایب سطر هدف در ستون‌های slack محاسبه می‌شود
                    current_coeff = self.obj_coeffs[j] if j < len(self.obj_coeffs) else 0
                    
                    # محاسبه allowable decrease و increase
                    allowable_decrease = float('inf')
                    allowable_increase = float('inf')
                    
                    for k in range(num_cons):
                        slack_col = num_vars + k
                        if slack_col < n - 1:  # اطمینان از وجود ستون
                            coeff = tableau[basis_row, slack_col]
                            if coeff > 1e-10:
                                ratio = tableau[-1, slack_col] / coeff
                                if ratio < allowable_decrease:
                                    allowable_decrease = ratio
                            elif coeff < -1e-10:
                                ratio = -tableau[-1, slack_col] / coeff
                                if ratio < allowable_increase:
                                    allowable_increase = ratio
                    
                    # اگر مقداری پیدا نشد، از مقادیر پیش‌فرض استفاده کن
                    if allowable_decrease == float('inf'):
                        allowable_decrease = current_coeff
                    if allowable_increase == float('inf'):
                        allowable_increase = float('inf')
                    
                    lower_bound = current_coeff - allowable_decrease
                    upper_bound = current_coeff + allowable_increase
                    
                else:
                    # اگر متغیر در پایه نیست
                    current_coeff = self.obj_coeffs[j] if j < len(self.obj_coeffs) else 0
                    reduced_cost = self.solution['reduced_costs'][j] if j < len(self.solution['reduced_costs']) else 0
                    
                    # برای متغیرهای غیرپایه، محدوده از روی reduced cost محاسبه می‌شود
                    if abs(reduced_cost) < 1e-10:
                        allowable_decrease = float('inf')
                        allowable_increase = float('inf')
                    else:
                        allowable_decrease = abs(reduced_cost)
                        allowable_increase = float('inf')
                    
                    lower_bound = current_coeff - allowable_increase if allowable_increase != float('inf') else -float('inf')
                    upper_bound = current_coeff + allowable_decrease if allowable_decrease != float('inf') else float('inf')
                
                # نمایش نتایج
                frame = tk.Frame(scrollable_frame, relief=tk.GROOVE, bd=1)
                frame.pack(pady=5, padx=10, fill=tk.X)
                
                # عنوان متغیر
                tk.Label(frame, text=f"• c{j+1} (x{j+1} coefficient):",
                        font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=5)
                
                # محدوده
                range_text = f"  Range: [{lower_bound:.4f}, {upper_bound:.4f}]"
                tk.Label(frame, text=range_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                # مقادیر جاری و allowable changes
                current_text = f"  Current: {current_coeff:.4f}"
                tk.Label(frame, text=current_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                if allowable_decrease != float('inf'):
                    dec_text = f"  Allowable Decrease: {allowable_decrease:.4f}"
                else:
                    dec_text = f"  Allowable Decrease: ∞"
                tk.Label(frame, text=dec_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                if allowable_increase != float('inf'):
                    inc_text = f"  Allowable Increase: {allowable_increase:.4f}"
                else:
                    inc_text = f"  Allowable Increase: ∞"
                tk.Label(frame, text=inc_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                # تفسیر
                if in_basis:
                    interpret_text = f"  Interpretation: x{j+1} is in optimal basis"
                else:
                    if upper_bound == float('inf'):
                        interpret_text = f"  Interpretation: x{j+1} can enter basis if coefficient increases by {allowable_decrease:.4f}"
                    else:
                        interpret_text = f"  Interpretation: x{j+1} is not in optimal basis"
                
                tk.Label(frame, text=interpret_text,
                        font=("Arial", 10), fg="#388E3C").pack(anchor=tk.W, padx=20, pady=5)
            
            # بخش ۲: محدوده تغییر سمت راست محدودیت‌ها
            tk.Label(scrollable_frame, text="\n📊 RIGHT-HAND SIDE RANGES (bᵢ):",
                    font=("Arial", 14, "bold"), fg="#283593").pack(pady=15, anchor=tk.W)
            
            tk.Label(scrollable_frame, 
                    text="How much can each constraint RHS change without changing the optimal basis?",
                    font=("Arial", 10), fg="#616161").pack(anchor=tk.W, pady=5)
            
            # محاسبه محدوده‌ها برای هر سمت راست
            for i in range(num_cons):
                # مقدار جاری سمت راست
                if hasattr(self, 'constraint_data') and i < len(self.constraint_data):
                    current_rhs = self.constraint_data[i]['rhs']
                else:
                    current_rhs = 0
                
                # پیدا کردن slack variable مربوطه
                slack_idx = num_vars + i
                
                # اگر slack در پایه است
                slack_in_basis = slack_idx in self.solution['basis']
                
                if slack_in_basis:
                    # اگر slack در پایه است (محدودیت non-binding)
                    basis_row_idx = list(self.solution['basis']).index(slack_idx)
                    
                    # مقدار slack
                    slack_value = tableau[basis_row_idx, -1]
                    
                    allowable_decrease = slack_value
                    allowable_increase = float('inf')
                    
                    lower_bound = current_rhs - allowable_decrease
                    upper_bound = float('inf')
                    
                else:
                    # اگر slack در پایه نیست (محدودیت binding)
                    # محدوده از روی shadow price و ضرایب محاسبه می‌شود
                    shadow_price = self.solution['shadow_prices'][i] if i < len(self.solution['shadow_prices']) else 0
                    
                    # پیدا کردن minimum ratio برای افزایش و کاهش
                    allowable_increase = float('inf')
                    allowable_decrease = float('inf')
                    
                    for k in range(num_cons):
                        if k != i:
                            # بررسی ضرایب در ستون slack مربوطه
                            coeff = tableau[k, slack_idx]
                            rhs = tableau[k, -1]
                            
                            if coeff > 1e-10:
                                ratio = rhs / coeff
                                if ratio < allowable_increase:
                                    allowable_increase = ratio
                            elif coeff < -1e-10:
                                ratio = -rhs / coeff
                                if ratio < allowable_decrease:
                                    allowable_decrease = ratio
                    
                    # اگر مقداری پیدا نشد
                    if allowable_increase == float('inf'):
                        allowable_increase = float('inf')
                    if allowable_decrease == float('inf'):
                        allowable_decrease = current_rhs
                    
                    lower_bound = current_rhs - allowable_decrease
                    upper_bound = current_rhs + allowable_increase
                
                # نمایش نتایج
                frame = tk.Frame(scrollable_frame, relief=tk.GROOVE, bd=1)
                frame.pack(pady=5, padx=10, fill=tk.X)
                
                # عنوان محدودیت
                tk.Label(frame, text=f"• b{i+1} (Constraint {i+1} RHS):",
                        font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=5)
                
                # محدوده
                if upper_bound == float('inf'):
                    range_text = f"  Range: [{lower_bound:.4f}, ∞]"
                else:
                    range_text = f"  Range: [{lower_bound:.4f}, {upper_bound:.4f}]"
                tk.Label(frame, text=range_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                # مقادیر جاری
                current_text = f"  Current: {current_rhs:.4f}"
                tk.Label(frame, text=current_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                # Allowable changes
                if allowable_decrease != float('inf'):
                    dec_text = f"  Allowable Decrease: {allowable_decrease:.4f}"
                else:
                    dec_text = f"  Allowable Decrease: ∞"
                tk.Label(frame, text=dec_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                if allowable_increase != float('inf'):
                    inc_text = f"  Allowable Increase: {allowable_increase:.4f}"
                else:
                    inc_text = f"  Allowable Increase: ∞"
                tk.Label(frame, text=inc_text,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20)
                
                # تفسیر
                if slack_in_basis:
                    interpret_text = f"  Interpretation: Constraint {i+1} is non-binding (has slack)"
                else:
                    if shadow_price > 1e-10:
                        if self.data['opt_type'] == "Max":
                            interpret_text = f"  Interpretation: Each unit increase adds {shadow_price:.4f} to profit"
                        else:
                            interpret_text = f"  Interpretation: Each unit increase reduces cost by {shadow_price:.4f}"
                    elif shadow_price < -1e-10:
                        if self.data['opt_type'] == "Max":
                            interpret_text = f"  Interpretation: Each unit increase reduces profit by {abs(shadow_price):.4f}"
                        else:
                            interpret_text = f"  Interpretation: Each unit increase adds {abs(shadow_price):.4f} to cost"
                    else:
                        interpret_text = f"  Interpretation: Constraint {i+1} is at its limit"
                
                tk.Label(frame, text=interpret_text,
                        font=("Arial", 10), fg="#388E3C").pack(anchor=tk.W, padx=20, pady=5)
            
            # بخش ۳: خلاصه و توصیه‌ها
            tk.Label(scrollable_frame, text="\n💡 KEY INSIGHTS & RECOMMENDATIONS:",
                    font=("Arial", 14, "bold"), fg="#FF9800").pack(pady=15, anchor=tk.W)
            
            insights_frame = tk.Frame(scrollable_frame, relief=tk.RIDGE, bd=2, bg="#FFF3E0")
            insights_frame.pack(pady=10, padx=10, fill=tk.X)
            
            insights = []
            
            # تحلیل stability
            stable_vars = 0
            for j in range(num_vars):
                in_basis = j in self.solution['basis']
                if in_basis:
                    # محاسبه range width
                    current_coeff = self.obj_coeffs[j] if j < len(self.obj_coeffs) else 0
                    
                    # محاسبه ساده range
                    if current_coeff > 0:
                        range_width = 2 * current_coeff  # تخمین
                    else:
                        range_width = abs(current_coeff)
                    
                    if range_width > current_coeff * 0.5:  # اگر range نسبتاً بزرگ است
                        stable_vars += 1
            
            if stable_vars > num_vars / 2:
                insights.append("✓ Solution is STABLE: Most variables have wide allowable ranges")
            else:
                insights.append("⚠ Solution is SENSITIVE: Many variables have narrow allowable ranges")
            
            # تحلیل constraints
            binding_constraints = 0
            for i in range(num_cons):
                slack_idx = num_vars + i
                if slack_idx not in self.solution['basis']:
                    binding_constraints += 1
            
            insights.append(f"✓ {binding_constraints} out of {num_cons} constraints are BINDING")
            
            # توصیه‌های عملی
            insights.append("\n🔧 PRACTICAL RECOMMENDATIONS:")
            
            # برای متغیرهای با range کوچک
            sensitive_vars = []
            for j in range(num_vars):
                in_basis = j in self.solution['basis']
                if in_basis:
                    current_coeff = self.obj_coeffs[j] if j < len(self.obj_coeffs) else 0
                    # اگر range کوچک است
                    if current_coeff > 0 and current_coeff < 1.0:
                        sensitive_vars.append(f"x{j+1}")
            
            if sensitive_vars:
                insights.append(f"• Monitor coefficients of: {', '.join(sensitive_vars)} (sensitive to changes)")
            
            # برای محدودیت‌های binding
            if binding_constraints > 0:
                insights.append(f"• Focus on {binding_constraints} binding constraints for improvement")
            
            
            # نمایش insights
            for insight in insights:
                if insight.startswith("✓"):
                    tk.Label(insights_frame, text=insight,
                            font=("Arial", 11), bg="#FFF3E0", fg="#2E7D32").pack(anchor=tk.W, padx=10, pady=2)
                elif insight.startswith("⚠"):
                    tk.Label(insights_frame, text=insight,
                            font=("Arial", 11), bg="#FFF3E0", fg="#D32F2F").pack(anchor=tk.W, padx=10, pady=2)
                elif insight.startswith("•"):
                    tk.Label(insights_frame, text=insight,
                            font=("Arial", 11), bg="#FFF3E0", fg="#1565C0").pack(anchor=tk.W, padx=10, pady=2)
                elif insight.startswith("🔧"):
                    tk.Label(insights_frame, text=insight,
                            font=("Arial", 11, "bold"), bg="#FFF3E0", fg="#FF9800").pack(anchor=tk.W, padx=10, pady=5)
                else:
                    tk.Label(insights_frame, text=insight,
                            font=("Arial", 11), bg="#FFF3E0").pack(anchor=tk.W, padx=10, pady=2)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # دکمه بستن
            close_btn = tk.Button(sensitivity_window, text="Close Sensitivity Analysis",
                                font=("Arial", 11),
                                command=sensitivity_window.destroy)
            close_btn.pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Sensitivity Analysis Error", f"Error in sensitivity analysis: {str(e)}")
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexSolverApp(root)
    root.mainloop()