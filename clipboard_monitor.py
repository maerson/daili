import wx
import win32api
import win32gui
import win32con
import win32clipboard
import re, os, sys, time
import json
from datetime import datetime
import signal


class TestFrame (wx.Frame):
    def __init__ (self):
        wx.Frame.__init__ (self, None, title="Clipboard viewer", size=(450,150))

        self.first   = True
        self.nextWnd = None
        self.hwnd    = self.GetHandle ()
        self.oldWndProc = win32gui.SetWindowLong (self.hwnd, win32con.GWL_WNDPROC, self.MyWndProc)

        self.data_list = []
        self.clipboard = wx.Clipboard()

        try:
            self.nextWnd = win32clipboard.SetClipboardViewer (self.hwnd)
        except win32api.error:
            if win32api.GetLastError () == 0: pass
            else: raise

    def MyWndProc (self, hWnd, msg, wParam, lParam):
        if msg == win32con.WM_CHANGECBCHAIN:
            self.OnChangeCBChain (msg, wParam, lParam)
        elif msg == win32con.WM_DRAWCLIPBOARD:
            self.OnDrawClipboard (msg, wParam, lParam)

        if msg == win32con.WM_DESTROY:
            if self.nextWnd:
               win32clipboard.ChangeClipboardChain (self.hwnd, self.nextWnd)
            else:
               win32clipboard.ChangeClipboardChain (self.hwnd, 0)

            win32api.SetWindowLong (self.hwnd, win32con.GWL_WNDPROC, self.oldWndProc)

            # 分析并保存结果
            self.save_proxies()
            self.clipboard.Close()


        return win32gui.CallWindowProc (self.oldWndProc, hWnd, msg, wParam, lParam)

    def OnChangeCBChain (self, msg, wParam, lParam):
        if self.nextWnd == wParam:
           self.nextWnd = lParam
        if self.nextWnd:
           win32api.SendMessage (self.nextWnd, msg, wParam, lParam)

    def OnDrawClipboard (self, msg, wParam, lParam):
        if self.first:
           self.first = False
        else:
           self.GetTextFromClipboard()
        if self.nextWnd:
           win32api.SendMessage (self.nextWnd, msg, wParam, lParam)


    # 好像被调用了2次
    def GetTextFromClipboard(self):
        if self.clipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
            data = wx.TextDataObject()
            self.clipboard.GetData(data)
            self.data_list.append(data.GetText())
            #print(data.GetText())


    def save_proxies(self):
        if len(self.data_list):
            outfile = open("web_proxies"+"_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".txt", 'w', -1, "utf-8")
            for text in self.data_list:
                # 分析IP地址
                re_ip_port_encode_result  = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,5})", text, re.M)
                re_ip_port_encode_result += re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})", text, re.M)
                if len(re_ip_port_encode_result) < 1:
                    # provider-idcloak_com.py
                    re_ip_port_encode_result  = re.findall("(\d{1,5})\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text, re.M)

                print("records: "+ str(len(re_ip_port_encode_result)))
                if len(re_ip_port_encode_result):
                    records = [{'host': ip, 'port': int(port)  } for ip, port in re_ip_port_encode_result]
                    for item in records:
                        outfile.write("%s\n" % json.dumps(item))
                    outfile.flush()

            self.data_list = []
            # 关闭文件
            outfile.close()


app   = wx.App()
frame = TestFrame()

frame.Show(True)
app.MainLoop()
