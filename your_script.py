import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import re

class PortManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("端口管理器")
        self.root.geometry("800x600")

        # 创建搜索框
        self.search_frame = ttk.Frame(root)
        self.search_frame.pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Label(self.search_frame, text="搜索端口:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_ports)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 创建列表
        self.tree = ttk.Treeview(root, columns=('PID', '进程名', '本地地址', '远程地址', '状态'))
        self.tree.heading('#0', text='')
        self.tree.heading('PID', text='PID')
        self.tree.heading('进程名', text='进程名')
        self.tree.heading('本地地址', text='本地地址')
        self.tree.heading('远程地址', text='远程地址')
        self.tree.heading('状态', text='状态')
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('PID', width=70)
        self.tree.column('进程名', width=120)
        self.tree.column('本地地址', width=200)
        self.tree.column('远程地址', width=200)
        self.tree.column('状态', width=100)
        
        self.tree.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_popup_menu)
        
        # 定时刷新端口列表
        self.refresh_ports()
        self.root.after(5000, self.refresh_ports)

    def get_process_name(self, pid):
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "未知进程"

    def refresh_ports(self):
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取所有网络连接
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            pid = conn.pid or 0
            process_name = self.get_process_name(pid) if pid else "系统"
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            
            self.tree.insert('', tk.END, values=(
                pid,
                process_name,
                laddr,
                raddr,
                conn.status
            ))
        
        # 应用当前的搜索过滤
        self.filter_ports()
        
        # 5秒后再次刷新
        self.root.after(5000, self.refresh_ports)

    def filter_ports(self, *args):
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            local_addr = str(values[2]).lower()
            
            # 如果搜索文本为空或者端口号匹配，则显示该项
            if not search_text or search_text in local_addr:
                self.tree.reattach(item, '', tk.END)
            else:
                self.tree.detach(item)

    def kill_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个进程")
            return
            
        pid = self.tree.item(selected_item[0])['values'][0]
        if pid == 0:
            messagebox.showwarning("警告", "无法结束系统进程")
            return
            
        try:
            process = psutil.Process(pid)
            process.terminate()
            messagebox.showinfo("成功", f"进程 {pid} 已被终止")
            self.refresh_ports()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("错误", f"无法终止进程: {str(e)}")

    def show_popup_menu(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="结束进程", command=self.kill_process)
            menu.post(event.x_root, event.y_root)

if __name__ == '__main__':
    root = tk.Tk()
    app = PortManagerApp(root)
    root.mainloop()
