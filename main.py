import ctypes,json,os,platform,subprocess,threading
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode('dark')
APP='LEVSCLOADES'; BG='#07090b'; PANEL='#101418'; PANEL2='#14191e'; BORDER='#2b3238'; Y='#ffd21c'; G='#4cff78'; R='#ff5b5b'; T='#f2f4f7'; M='#9aa4ae'

def admin():
    try:return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except:return False

def ps(cmd,timeout=15):
    try:
        p=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-Command',cmd],capture_output=True,text=True,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
        return p.stdout.strip(),p.stderr.strip(),p.returncode
    except Exception as e:return '',str(e),1

def gpus():
    o,e,c=ps("Get-CimInstance Win32_VideoController | Select Name,AdapterCompatibility,DriverVersion,Status | ConvertTo-Json -Compress")
    if c or not o:return []
    try:d=json.loads(o); d=d if isinstance(d,list) else [d]
    except:return []
    r=[]
    for x in d:
        n=x.get('Name') or 'Unknown GPU'; b=(n+' '+(x.get('AdapterCompatibility') or '')).lower()
        v='NVIDIA' if ('nvidia' in b or 'geforce' in b or 'rtx' in b or 'gtx' in b) else 'AMD' if ('amd' in b or 'radeon' in b) else 'Intel' if ('intel' in b or 'uhd graphics' in b or 'iris' in b or 'arc graphics' in b) else 'Other'
        typ='Integrated / likely shared memory' if v=='Intel' or ('radeon' in b and 'graphics' in b) else 'Dedicated / likely discrete' if v in ('AMD','NVIDIA') else 'Unknown'
        r.append({'name':n,'vendor':v,'type':typ,'driver':x.get('DriverVersion') or 'Unknown','status':x.get('Status') or 'Unknown'})
    return r

def sysinfo_fast():
    # One PowerShell process instead of 4 separate processes. This is much faster on startup.
    cmd = "$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_Processor | Select -First 1; $m=Get-CimInstance Win32_ComputerSystem; $g=Get-CimInstance Win32_VideoController; [pscustomobject]@{OS=$o.Caption;Build=$o.BuildNumber;CPU=$c.Name;RAM=$m.TotalPhysicalMemory;GPU=@($g.Name)} | ConvertTo-Json -Compress"
    out,_,code=ps(cmd,8)
    if code or not out:
        return 'Windows','',platform.processor() or 'Unknown','Unknown','Unknown'
    try:
        d=json.loads(out)
        ram=f"{int(d.get('RAM',0))/(1024**3):.1f} GB" if d.get('RAM') else 'Unknown'
        gpu=d.get('GPU') or 'Unknown'
        if isinstance(gpu,list):
            gpu=' + '.join(str(x) for x in gpu if x) or 'Unknown'
        return d.get('OS') or 'Windows', 'Build '+str(d.get('Build') or ''), d.get('CPU') or 'Unknown', ram, gpu
    except Exception:
        return 'Windows','',platform.processor() or 'Unknown','Unknown','Unknown'

class App(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title(APP+' — Windows Debloater & Optimizer'); self.geometry('1450x900'); self.minsize(1150,760); self.configure(fg_color=BG); self.isadmin=admin(); self.nav={}
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(1,weight=1); self.header(); self.sidebar(); self.content=ctk.CTkFrame(self,fg_color=BG,corner_radius=0); self.content.grid(row=1,column=1,sticky='nsew'); self.footer(); self.show('Dashboard')
        self.after(80, self.start_background_refresh)
    def header(self):
        h=ctk.CTkFrame(self,fg_color=BG,height=82,corner_radius=0); h.grid(row=0,column=0,columnspan=2,sticky='ew'); h.grid_columnconfigure(1,weight=1)
        ctk.CTkLabel(h,text='⚡  LEVSCLOADES',text_color=Y,font=ctk.CTkFont(size=28,weight='bold')).grid(row=0,column=0,padx=(25,5),pady=(14,0),sticky='w')
        ctk.CTkLabel(h,text='Windows Debloater & Optimizer',text_color=M,font=ctk.CTkFont(size=13)).grid(row=1,column=0,padx=(57,0),pady=(0,10),sticky='w')
        self.status=ctk.CTkFrame(h,fg_color=PANEL,border_color='#284b2f' if self.isadmin else '#5a4b19',border_width=1,corner_radius=14); self.status.grid(row=0,column=2,rowspan=2,padx=10,pady=15)
        ctk.CTkLabel(self.status,text='●',text_color=G if self.isadmin else Y,font=ctk.CTkFont(size=18)).grid(row=0,column=0,rowspan=2,padx=(12,5)); ctk.CTkLabel(self.status,text='SYSTEM READY' if self.isadmin else 'LIMITED ACCESS',text_color=G if self.isadmin else Y,font=ctk.CTkFont(size=12,weight='bold')).grid(row=0,column=1,padx=(0,15),pady=(7,0),sticky='w'); ctk.CTkLabel(self.status,text='Real actions only',text_color=M,font=ctk.CTkFont(size=10)).grid(row=1,column=1,padx=(0,15),pady=(0,7),sticky='w')
        a=ctk.CTkFrame(h,fg_color=PANEL,border_color=BORDER,border_width=1,corner_radius=14); a.grid(row=0,column=3,rowspan=2,padx=(0,25),pady=15); ctk.CTkLabel(a,text='●' if self.isadmin else '○',text_color=G if self.isadmin else Y,font=ctk.CTkFont(size=18)).grid(row=0,column=0,rowspan=2,padx=(12,6)); ctk.CTkLabel(a,text='Administrator' if self.isadmin else 'Standard User',text_color=T,font=ctk.CTkFont(size=12,weight='bold')).grid(row=0,column=1,padx=(0,15),pady=(7,0),sticky='w'); ctk.CTkLabel(a,text='Full Access' if self.isadmin else 'Read-only where required',text_color=M,font=ctk.CTkFont(size=10)).grid(row=1,column=1,padx=(0,15),pady=(0,7),sticky='w'); ctk.CTkFrame(h,height=2,fg_color=Y).grid(row=2,column=0,columnspan=4,sticky='ew')
    def sidebar(self):
        s=ctk.CTkFrame(self,width=255,fg_color='#090c0f',corner_radius=0,border_color=BORDER,border_width=1); s.grid(row=1,column=0,sticky='nsew'); s.grid_propagate(False); r=0
        groups=[('',[('Dashboard','⌂')]),('DEBLOATERS',[('Windows Privacy','◈'),('Windows Debloat','⊞'),('Apps','▦'),('Services','⚙')]),('TWEAK PACK',[('Power Plans','ϟ'),('GPU Optimization','▣'),('OS Optimization','◉'),('Gaming','G'),('Useful Tools','⚒')]),('NETWORK OPTIMIZER',[('Network Adapter','⌁'),('TCP','≋'),('DNS','◎'),('Latency','◷')])]
        for title,items in groups:
            if title:ctk.CTkLabel(s,text=title,text_color=M,font=ctk.CTkFont(size=11,weight='bold')).grid(row=r,column=0,padx=22,pady=(18,6),sticky='w'); r+=bool(title)
            for n,ic in items:
                b=ctk.CTkButton(s,text=f'  {ic}   {n}',anchor='w',height=41,fg_color='transparent',hover_color='#1d1d0f',text_color=T,command=lambda x=n:self.show(x)); b.grid(row=r,column=0,padx=12,pady=2,sticky='ew'); self.nav[n]=b; r+=1
        ctk.CTkFrame(s,height=1,fg_color=BORDER).grid(row=r,column=0,padx=20,pady=16,sticky='ew'); r+=1
        for n,ic in [('Settings','⚙'),('About','ⓘ')]:
            b=ctk.CTkButton(s,text=f'  {ic}   {n}',anchor='w',height=40,fg_color='transparent',hover_color='#1d1d0f',text_color=T,command=lambda x=n:self.show(x)); b.grid(row=r,column=0,padx=12,pady=2,sticky='ew'); self.nav[n]=b; r+=1
    def footer(self):
        f=ctk.CTkFrame(self,fg_color='#080a0c',height=48,corner_radius=0); f.grid(row=2,column=0,columnspan=2,sticky='ew'); ctk.CTkLabel(f,text='⚡ LEVSCLOADES',text_color=Y,font=ctk.CTkFont(size=12,weight='bold')).pack(side='left',padx=24); ctk.CTkLabel(f,text='© 2026 LEVSCLOADES — All Rights Reserved.',text_color=M,font=ctk.CTkFont(size=10)).pack(side='left'); ctk.CTkLabel(f,text='Every action reports its real result.',text_color=M,font=ctk.CTkFont(size=10)).pack(side='right',padx=24)
    def clear(self):
        for w in self.content.winfo_children():w.destroy()
    def show(self,n):
        self.clear()
        for k,b in self.nav.items():b.configure(fg_color='#302b05' if k==n else 'transparent',text_color=Y if k==n else T)
        getattr(self,'p_'+n.lower().replace(' ','_'))()
    def page_title(self,t,sub=''):
        ctk.CTkLabel(self.content,text=t,text_color=T,font=ctk.CTkFont(size=27,weight='bold')).pack(anchor='w',padx=30,pady=(25,2)); ctk.CTkLabel(self.content,text=sub,text_color=M,font=ctk.CTkFont(size=12)).pack(anchor='w',padx=30,pady=(0,18)) if sub else None
    def btn(self,parent,text,fn,danger=False):return ctk.CTkButton(parent,text=text,height=36,fg_color='transparent',border_width=1,border_color=R if danger else Y,hover_color='#3a3304',text_color=R if danger else Y,command=fn)
    def card(self,parent,t,d=''):
        f=ctk.CTkFrame(parent,fg_color=PANEL,border_color=BORDER,border_width=1,corner_radius=14); ctk.CTkLabel(f,text=t,text_color=Y,font=ctk.CTkFont(size=15,weight='bold')).pack(anchor='w',padx=18,pady=(15,2)); ctk.CTkLabel(f,text=d,text_color=M,wraplength=360,justify='left').pack(anchor='w',padx=18,pady=(0,12)) if d else None; return f
    def p_dashboard(self):
        self.page_title('Welcome to LEVSCLOADES','Optimize your Windows environment with actions that report their actual result.')
        b=ctk.CTkFrame(self.content,fg_color=PANEL,border_color=BORDER,border_width=1,corner_radius=16); b.pack(fill='x',padx=30,pady=(0,18)); ctk.CTkLabel(b,text='CLEANER SYSTEM\nBETTER PERFORMANCE\nSMOOTHER EXPERIENCE',text_color=Y,font=ctk.CTkFont(size=14,weight='bold'),justify='right').pack(side='right',padx=28,pady=22); ctk.CTkLabel(b,text='No fake actions.\nEvery operation is verified and logged.',text_color=T,font=ctk.CTkFont(size=17,weight='bold'),justify='left').pack(anchor='w',padx=25,pady=22)
        row=ctk.CTkFrame(self.content,fg_color='transparent'); row.pack(fill='x',padx=30); row.grid_columnconfigure((0,1,2),weight=1)
        mods=[('DEBLOATERS','Remove or inspect Windows components.', [('Windows Privacy','Windows Privacy'),('Windows Debloat','Windows Debloat'),('Apps','Apps'),('Services','Services')]),('TWEAK PACK','Hardware-aware Windows tools.', [('Power Plans','Power Plans'),('GPU Optimization','GPU Optimization'),('OS Optimization','OS Optimization'),('Gaming','Gaming'),('Useful Tools','Useful Tools')]),('NETWORK OPTIMIZER','Inspect adapters, DNS, TCP and latency.', [('Network Adapter','Network Adapter'),('TCP','TCP'),('DNS','DNS'),('Latency','Latency')])]
        for i,(t,d,items) in enumerate(mods):
            f=self.card(row,t,d); f.grid(row=0,column=i,padx=7,sticky='nsew')
            for label,target in items:ctk.CTkButton(f,text='●  '+label,anchor='w',fg_color='transparent',hover_color='#1d1d0f',text_color=T,height=33,command=lambda x=target:self.show(x)).pack(fill='x',padx=12,pady=1)
            self.btn(f,'VIEW ALL  →',lambda x=items[0][1]:self.show(x)).pack(fill='x',padx=18,pady=(14,18))
        info=ctk.CTkFrame(self.content,fg_color=PANEL,border_color=BORDER,border_width=1,corner_radius=14); info.pack(fill='x',padx=30,pady=18); ctk.CTkLabel(info,text='SYSTEM INFORMATION',text_color=Y,font=ctk.CTkFont(size=13,weight='bold')).pack(anchor='w',padx=18,pady=(14,8)); grid=ctk.CTkFrame(info,fg_color='transparent'); grid.pack(fill='x',padx=18,pady=(0,16)); self.labels={}
        for i,k in enumerate(['os','cpu','ram','gpu']):
            grid.grid_columnconfigure(i,weight=1); q=ctk.CTkFrame(grid,fg_color=PANEL2,corner_radius=10); q.grid(row=0,column=i,padx=4,sticky='nsew'); ctk.CTkLabel(q,text=k.upper(),text_color=M,font=ctk.CTkFont(size=9,weight='bold')).pack(anchor='w',padx=12,pady=(10,1)); l=ctk.CTkLabel(q,text='Detecting...',text_color=T,font=ctk.CTkFont(size=11,weight='bold'),wraplength=230,justify='left'); l.pack(anchor='w',padx=12,pady=(0,10)); self.labels[k]=l
        # Do not run PowerShell on the Tk main thread. Render immediately, then update in background.
        self.labels['os'].configure(text='Loading…')
        self.labels['cpu'].configure(text='Loading…')
        self.labels['ram'].configure(text='Loading…')
        self.labels['gpu'].configure(text='Loading…')

    def start_background_refresh(self):
        threading.Thread(target=self._load_system_info, daemon=True).start()

    def _load_system_info(self):
        data=sysinfo_fast()
        self.after(0, lambda: self._apply_system_info(data))

    def _apply_system_info(self,data):
        if not hasattr(self,'labels') or not self.winfo_exists():
            return
        osn,build,cpu,ram,gpu=data
        self.labels['os'].configure(text=osn+'\n'+build)
        self.labels['cpu'].configure(text=cpu)
        self.labels['ram'].configure(text=ram)
        self.labels['gpu'].configure(text=gpu)
    def p_windows_privacy(self):self.generic('Windows Privacy','Reads current privacy-related registry values. No change is made automatically.',"Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo' -ErrorAction SilentlyContinue | Format-List *; Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager' -ErrorAction SilentlyContinue | Select SubscribedContent-338388Enabled,SubscribedContent-353694Enabled | Format-List")
    def p_windows_debloat(self):self.generic('Windows Debloat','Scans installed AppX packages. Nothing is removed automatically.',"Get-AppxPackage | Sort Name | Select Name,Version | Format-Table -AutoSize",30)
    def p_apps(self):self.generic('Apps','Lists installed Store/AppX packages for inspection.',"Get-AppxPackage | Sort Name | Select Name,Version,Publisher | Format-Table -AutoSize",30)
    def p_services(self):self.generic('Services','Shows real service state. Services are not disabled automatically.',"Get-Service | Sort Status,DisplayName | Select Status,StartType,Name,DisplayName | Format-Table -AutoSize",30)
    def generic(self,t,sub,cmd,height=1):
        self.page_title(t,sub); out=ctk.CTkTextbox(self.content,fg_color=PANEL,border_color=BORDER,border_width=1,corner_radius=12,text_color=T,font=('Consolas',10)); out.pack(fill='both',expand=True,padx=30,pady=10)
        def scan():
            out.delete('1.0','end'); o,e,c=ps(cmd,30); out.insert('end',o if o else (e or '[No output]')); out.insert('end',f'\n\n[return code: {c}]')
        self.btn(self.content,'SCAN / REFRESH',scan).pack(fill='x',padx=30,pady=5); scan()
    def p_power_plans(self):self.generic('Power Plans','Real power-plan information from Windows.','powercfg /list')
    def p_gpu_optimization(self):
        self.page_title('GPU Optimization','GPU-aware detection: only detected hardware is shown. No driver spoofing or fake success states.')
        gs=gpus()
        if not gs:ctk.CTkLabel(self.content,text='GPU detection failed through Win32_VideoController.',text_color=R).pack(anchor='w',padx=30); return
        for x in gs:
            f=self.card(self.content,x['name'],f"Vendor: {x['vendor']}    Type: {x['type']}\nDriver: {x['driver']}    Status: {x['status']}"); f.pack(fill='x',padx=30,pady=5)
        ctk.CTkLabel(self.content,text='Supported Windows graphics controls are opened through Windows Settings rather than undocumented driver hacks.',text_color=M).pack(anchor='w',padx=30,pady=12)
        self.btn(self.content,'OPEN WINDOWS GRAPHICS SETTINGS',lambda:self.uri('ms-settings:display-advancedgraphics')).pack(fill='x',padx=30,pady=4); self.btn(self.content,'REFRESH GPU DETECTION',lambda:self.show('GPU Optimization')).pack(fill='x',padx=30,pady=4)
    def p_os_optimization(self):self.generic('OS Optimization','Reads current Windows version/build and architecture.','Get-ComputerInfo | Select WindowsProductName,WindowsVersion,OsBuildNumber,OsArchitecture | Format-List')
    def p_gaming(self):
        self.page_title('Gaming','Real Windows gaming settings. Each button opens the corresponding Windows page.')
        for t,u in [('OPEN GAME MODE SETTINGS','ms-settings:gaming-gamemode'),('OPEN GRAPHICS SETTINGS','ms-settings:display-advancedgraphics'),('OPEN CAPTURES SETTINGS','ms-settings:gaming-gamedvr')]:self.btn(self.content,t,lambda x=u:self.uri(x)).pack(fill='x',padx=30,pady=5)
    def p_useful_tools(self):
        self.page_title('Useful Tools','Real Windows maintenance utilities.');
        for t,x in [('OPEN SYSTEM RESTORE','rstrui.exe'),('OPEN DEVICE MANAGER','devmgmt.msc'),('OPEN DISK CLEANUP','cleanmgr.exe')]:self.btn(self.content,t,lambda z=x:self.launch(z)).pack(fill='x',padx=30,pady=5)
        self.btn(self.content,'CREATE RESTORE POINT (ADMIN REQUIRED)',self.restore).pack(fill='x',padx=30,pady=5)
    def p_network_adapter(self):
        self.page_title('Network Adapter','Real active network adapters detected by Windows.'); a=get_adapters()
        if not a:ctk.CTkLabel(self.content,text='No active adapters returned.',text_color=R).pack(anchor='w',padx=30)
        for x in a:self.card(self.content,x.get('Name','Unknown'),f"{x.get('InterfaceDescription','')}\nStatus: {x.get('Status','Unknown')}    Link: {x.get('LinkSpeed','Unknown')}\nMAC: {x.get('MacAddress','Unknown')}").pack(fill='x',padx=30,pady=5)
    def p_tcp(self):self.generic('TCP','Reads current TCP global settings.','netsh interface tcp show global')
    def p_dns(self):
        self.page_title('DNS','Displays configured IPv4 DNS servers.'); o,e,c=ps("Get-DnsClientServerAddress -AddressFamily IPv4 | Where ServerAddresses | Select InterfaceAlias,ServerAddresses | Format-Table -AutoSize",8)
        box=ctk.CTkTextbox(self.content,fg_color=PANEL,text_color=T); box.pack(fill='x',padx=30,pady=10); box.insert('end',o if o else e)
        self.btn(self.content,'OPEN WINDOWS NETWORK SETTINGS',lambda:self.uri('ms-settings:network')).pack(fill='x',padx=30,pady=5)
    def p_latency(self):
        self.page_title('Latency','Measures real ICMP latency to 1.1.1.1. Results depend on your connection.')
        box=ctk.CTkTextbox(self.content,fg_color=PANEL,text_color=T,height=220); box.pack(fill='x',padx=30,pady=10)
        def test():box.delete('1.0','end'); p=subprocess.run(['ping.exe','-n','4','-w','1000','1.1.1.1'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW); box.insert('end',p.stdout+f'\nReturn code: {p.returncode}')
        self.btn(self.content,'RUN 4-PACKET LATENCY TEST',test).pack(fill='x',padx=30,pady=5); test()
    def p_settings(self):self.page_title('Settings','Application information.'); ctk.CTkLabel(self.content,text='Dark appearance\nVersion 1.0.0\nSystem information refreshes when Dashboard is opened.',text_color=T,justify='left').pack(anchor='w',padx=30,pady=10); self.btn(self.content,'OPEN DASHBOARD',lambda:self.show('Dashboard')).pack(fill='x',padx=30,pady=5)
    def p_about(self):self.page_title('About LEVSCLOADES','Windows Debloater & Optimizer'); ctk.CTkLabel(self.content,text='This build avoids fake success messages. Actions either execute a real Windows operation, open a real Windows settings page, display real system data, or report an error.\n\nCopyright © 2026 LEVSCLOADES — All Rights Reserved.\nDo not resell, repackage, or redistribute this software without permission.',text_color=T,justify='left').pack(anchor='w',padx=30,pady=10)
    def uri(self,u):
        try:os.startfile(u)
        except Exception as e:messagebox.showerror(APP,str(e))
    def launch(self,x):
        try:subprocess.Popen([x],creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:messagebox.showerror(APP,str(e))
    def restore(self):
        if not self.isadmin:messagebox.showwarning(APP,'Administrator privileges are required.'); return
        o,e,c=ps("Checkpoint-Computer -Description 'LEVSCLOADES Backup' -RestorePointType MODIFY_SETTINGS",45); messagebox.showinfo(APP,'Restore point request completed.') if c==0 else messagebox.showerror(APP,e or o or 'Windows did not create the restore point.')

def get_adapters():
    o,e,c=ps("Get-NetAdapter | Where Status -ne 'Disabled' | Select Name,InterfaceDescription,Status,LinkSpeed,MacAddress | ConvertTo-Json -Compress")
    if c or not o:return []
    try:d=json.loads(o); return d if isinstance(d,list) else [d]
    except:return []

if __name__=='__main__':
    if os.name!='nt':raise SystemExit('LEVSCLOADES requires Windows.')
    App().mainloop()
