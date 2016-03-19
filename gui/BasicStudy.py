# -------------------------------------------------------------------------------
# Name:        BasicStudy.py
# Purpose:     study python gui basics
#
# Author:      qin.shuq
#
# Created:
#-------------------------------------------------------------------------------
# -*- coding: utf8 -*-

import os
import wx
import util.Utils as util
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(480,480))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()

        filemenu = wx.Menu()
        openFileMenuItem = filemenu.Append(wx.ID_FILECTRL, '&OPEN', 'open file...')
        editMenuItem = filemenu.Append(wx.ID_EDIT, '&EDIT', 'Edit the text')
        aboutMenuItem = filemenu.Append(wx.ID_ABOUT, '&ABOUT', 'Information about the software')
        filemenu.AppendSeparator()
        exitMenuItem = filemenu.Append(wx.ID_EXIT, '&EXIT', 'quit')

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, '&File')
        self.SetMenuBar(menuBar)
        self.Show(True)
        self.Bind(wx.EVT_MENU, self.onOpenFile, openFileMenuItem)
        self.Bind(wx.EVT_MENU, self.onEdit, editMenuItem)
        self.Bind(wx.EVT_MENU, self.onAbout, aboutMenuItem)
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)

    def onOpenFile(self, event):
        dig = wx.FileDialog(self, 'Choose a file', '', '', '*.*', wx.OPEN)
        if dig.ShowModal() == wx.ID_OK:
            filename = dig.GetFilename()
            dirname = dig.GetDirectory()
            f = open(os.path.join(dirname, filename), 'r')
            self.control.SetValue(f.read())
            f.close()
        dig.Destroy()

    def onEdit(self, event):
        self.control.write(str(util.obtainEventInfo(event)))

    def onAbout(self, event):
        dig = wx.MessageDialog(self, 'A simple demo for python gui study', 'About the software',  wx.OK)
        dig.ShowModal()
        dig.Destroy()

    def onExit(self, event):
        self.Close(True)

def main():
    app = wx.App(False)
    frame = MainWindow(None, 'Python GUI Basics')
    app.MainLoop()



if __name__ == '__main__':
    main()