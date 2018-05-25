import Main
import wx

app = wx.PySimpleApp()

frame = Main.MainWindow()
frame.Center()
frame.Show()

print('Hello Console! ProjectManager is running!')
app.MainLoop()