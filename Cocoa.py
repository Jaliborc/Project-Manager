import wx.lib.buttons
import wx

class ImageButton( wx.lib.buttons.GenButton ):
	def __init__( self, *args, **kargs):
		wx.lib.buttons.GenButton.__init__(self, size = self.imageSize, *args, **kargs)

	def OnPaint(self, event):
		w, h = self.GetSize()
		dc = wx.PaintDC(self)
		
		if self.up:
			dc.DrawBitmap(wx.Bitmap(self.upImage), 0, 0)
		else:
			dc.DrawBitmap(wx.Bitmap(self.downImage), 0, 0)
			
class LightPlus( ImageButton ):
 	upImage = "LightPlus-Up.png"
 	downImage = "LightPlus-Down.png"
 	imageSize = (23, 21)
 	
class LightMinus( ImageButton ):
 	upImage = "LightMinus-Up.png"
 	downImage = "LightMinus-Down.png"
 	imageSize = (23, 21)