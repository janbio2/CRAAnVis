# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuOpen_Recent = QtWidgets.QMenu(parent=self.menuFile)
        self.menuOpen_Recent.setEnabled(False)
        self.menuOpen_Recent.setObjectName("menuOpen_Recent")
        self.menuEdit = QtWidgets.QMenu(parent=self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(parent=self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuWindow = QtWidgets.QMenu(parent=self.menubar)
        self.menuWindow.setObjectName("menuWindow")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuTree = QtWidgets.QMenu(parent=self.menubar)
        self.menuTree.setObjectName("menuTree")
        self.menuArrays = QtWidgets.QMenu(parent=self.menubar)
        self.menuArrays.setObjectName("menuArrays")
        self.menuColors = QtWidgets.QMenu(parent=self.menubar)
        self.menuColors.setObjectName("menuColors")
        self.menuColor_By_Metadata = QtWidgets.QMenu(parent=self.menuColors)
        self.menuColor_By_Metadata.setObjectName("menuColor_By_Metadata")
        self.menuColor_By_Imported_Color_Map = QtWidgets.QMenu(parent=self.menuColors)
        self.menuColor_By_Imported_Color_Map.setEnabled(False)
        self.menuColor_By_Imported_Color_Map.setObjectName("menuColor_By_Imported_Color_Map")
        MainWindow.setMenuBar(self.menubar)
        self.actionExport_as_Pdf = QtGui.QAction(parent=MainWindow)
        self.actionExport_as_Pdf.setEnabled(False)
        self.actionExport_as_Pdf.setObjectName("actionExport_as_Pdf")
        self.actionExport_as_Png = QtGui.QAction(parent=MainWindow)
        self.actionExport_as_Png.setEnabled(False)
        self.actionExport_as_Png.setObjectName("actionExport_as_Png")
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        self.actionAbout.setEnabled(False)
        self.actionAbout.setObjectName("actionAbout")
        self.actionUndo = QtGui.QAction(parent=MainWindow)
        self.actionUndo.setEnabled(False)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtGui.QAction(parent=MainWindow)
        self.actionRedo.setEnabled(False)
        self.actionRedo.setObjectName("actionRedo")
        self.actionCopy_Image = QtGui.QAction(parent=MainWindow)
        self.actionCopy_Image.setEnabled(False)
        self.actionCopy_Image.setObjectName("actionCopy_Image")
        self.actionClear = QtGui.QAction(parent=MainWindow)
        self.actionClear.setEnabled(True)
        self.actionClear.setObjectName("actionClear")
        self.actionZoom_In = QtGui.QAction(parent=MainWindow)
        self.actionZoom_In.setObjectName("actionZoom_In")
        self.actionZoom_Out = QtGui.QAction(parent=MainWindow)
        self.actionZoom_Out.setObjectName("actionZoom_Out")
        self.actionShow_Array = QtGui.QAction(parent=MainWindow)
        self.actionShow_Array.setObjectName("actionShow_Array")
        self.actionShow_Tree = QtGui.QAction(parent=MainWindow)
        self.actionShow_Tree.setObjectName("actionShow_Tree")
        self.actionsmyck = QtGui.QAction(parent=MainWindow)
        self.actionsmyck.setObjectName("actionsmyck")
        self.action246 = QtGui.QAction(parent=MainWindow)
        self.action246.setObjectName("action246")
        self.actionSingle_Color_Mode = QtGui.QAction(parent=MainWindow)
        self.actionSingle_Color_Mode.setCheckable(True)
        self.actionSingle_Color_Mode.setChecked(False)
        self.actionSingle_Color_Mode.setObjectName("actionSingle_Color_Mode")
        self.actionTwo_Color_Mode = QtGui.QAction(parent=MainWindow)
        self.actionTwo_Color_Mode.setCheckable(True)
        self.actionTwo_Color_Mode.setChecked(False)
        self.actionTwo_Color_Mode.setObjectName("actionTwo_Color_Mode")
        self.actionMinimize = QtGui.QAction(parent=MainWindow)
        self.actionMinimize.setObjectName("actionMinimize")
        self.actionZoom = QtGui.QAction(parent=MainWindow)
        self.actionZoom.setObjectName("actionZoom")
        self.actionSettings = QtGui.QAction(parent=MainWindow)
        self.actionSettings.setEnabled(False)
        self.actionSettings.setObjectName("actionSettings")
        self.actiontest = QtGui.QAction(parent=MainWindow)
        self.actiontest.setObjectName("actiontest")
        self.actiontest_2 = QtGui.QAction(parent=MainWindow)
        self.actiontest_2.setObjectName("actiontest_2")
        self.actionshow_tree = QtGui.QAction(parent=MainWindow)
        self.actionshow_tree.setCheckable(True)
        self.actionshow_tree.setChecked(True)
        self.actionshow_tree.setEnabled(False)
        self.actionshow_tree.setObjectName("actionshow_tree")
        self.actionShow_Spacers = QtGui.QAction(parent=MainWindow)
        self.actionShow_Spacers.setCheckable(True)
        self.actionShow_Spacers.setChecked(True)
        self.actionShow_Spacers.setEnabled(False)
        self.actionShow_Spacers.setObjectName("actionShow_Spacers")
        self.actionShow_Template = QtGui.QAction(parent=MainWindow)
        self.actionShow_Template.setCheckable(True)
        self.actionShow_Template.setChecked(True)
        self.actionShow_Template.setEnabled(False)
        self.actionShow_Template.setObjectName("actionShow_Template")
        self.actionShow_Original_Names = QtGui.QAction(parent=MainWindow)
        self.actionShow_Original_Names.setCheckable(True)
        self.actionShow_Original_Names.setChecked(True)
        self.actionShow_Original_Names.setEnabled(False)
        self.actionShow_Original_Names.setObjectName("actionShow_Original_Names")
        self.actionShow_Edge_Length = QtGui.QAction(parent=MainWindow)
        self.actionShow_Edge_Length.setCheckable(True)
        self.actionShow_Edge_Length.setChecked(False)
        self.actionShow_Edge_Length.setEnabled(False)
        self.actionShow_Edge_Length.setObjectName("actionShow_Edge_Length")
        self.actionShow_Evolutionary_Events = QtGui.QAction(parent=MainWindow)
        self.actionShow_Evolutionary_Events.setCheckable(True)
        self.actionShow_Evolutionary_Events.setChecked(True)
        self.actionShow_Evolutionary_Events.setEnabled(False)
        self.actionShow_Evolutionary_Events.setObjectName("actionShow_Evolutionary_Events")
        self.actionPool_Evolutionary_Events = QtGui.QAction(parent=MainWindow)
        self.actionPool_Evolutionary_Events.setCheckable(True)
        self.actionPool_Evolutionary_Events.setChecked(True)
        self.actionPool_Evolutionary_Events.setEnabled(True)
        self.actionPool_Evolutionary_Events.setObjectName("actionPool_Evolutionary_Events")
        self.actionShow_Short_Tree = QtGui.QAction(parent=MainWindow)
        self.actionShow_Short_Tree.setCheckable(True)
        self.actionShow_Short_Tree.setChecked(False)
        self.actionShow_Short_Tree.setEnabled(False)
        self.actionShow_Short_Tree.setObjectName("actionShow_Short_Tree")
        self.actiontest_3 = QtGui.QAction(parent=MainWindow)
        self.actiontest_3.setObjectName("actiontest_3")
        self.actionHorizontal_Color_Split = QtGui.QAction(parent=MainWindow)
        self.actionHorizontal_Color_Split.setObjectName("actionHorizontal_Color_Split")
        self.actionInner_Outer_Color_Split = QtGui.QAction(parent=MainWindow)
        self.actionInner_Outer_Color_Split.setObjectName("actionInner_Outer_Color_Split")
        self.actionSplit_Event_Colors_Horizontal = QtGui.QAction(parent=MainWindow)
        self.actionSplit_Event_Colors_Horizontal.setCheckable(True)
        self.actionSplit_Event_Colors_Horizontal.setChecked(False)
        self.actionSplit_Event_Colors_Horizontal.setEnabled(True)
        self.actionSplit_Event_Colors_Horizontal.setObjectName("actionSplit_Event_Colors_Horizontal")
        self.actionSplit_Event_Colors_InnerOuter = QtGui.QAction(parent=MainWindow)
        self.actionSplit_Event_Colors_InnerOuter.setCheckable(True)
        self.actionSplit_Event_Colors_InnerOuter.setChecked(False)
        self.actionSplit_Event_Colors_InnerOuter.setEnabled(True)
        self.actionSplit_Event_Colors_InnerOuter.setObjectName("actionSplit_Event_Colors_InnerOuter")
        self.actiontest_4 = QtGui.QAction(parent=MainWindow)
        self.actiontest_4.setObjectName("actiontest_4")
        self.actionShow_Spacerfrequency_at_Distance = QtGui.QAction(parent=MainWindow)
        self.actionShow_Spacerfrequency_at_Distance.setCheckable(True)
        self.actionShow_Spacerfrequency_at_Distance.setChecked(True)
        self.actionShow_Spacerfrequency_at_Distance.setEnabled(False)
        self.actionShow_Spacerfrequency_at_Distance.setObjectName("actionShow_Spacerfrequency_at_Distance")
        self.actionShow_Original_Tree = QtGui.QAction(parent=MainWindow)
        self.actionShow_Original_Tree.setCheckable(True)
        self.actionShow_Original_Tree.setChecked(True)
        self.actionShow_Original_Tree.setEnabled(False)
        self.actionShow_Original_Tree.setObjectName("actionShow_Original_Tree")
        self.actionShow_Root_Events_as_Array = QtGui.QAction(parent=MainWindow)
        self.actionShow_Root_Events_as_Array.setCheckable(True)
        self.actionShow_Root_Events_as_Array.setChecked(True)
        self.actionShow_Root_Events_as_Array.setEnabled(False)
        self.actionShow_Root_Events_as_Array.setObjectName("actionShow_Root_Events_as_Array")
        self.actionCollapse_Leaf_Acquisitions_in_Array = QtGui.QAction(parent=MainWindow)
        self.actionCollapse_Leaf_Acquisitions_in_Array.setCheckable(True)
        self.actionCollapse_Leaf_Acquisitions_in_Array.setEnabled(False)
        self.actionCollapse_Leaf_Acquisitions_in_Array.setObjectName("actionCollapse_Leaf_Acquisitions_in_Array")
        self.actionExtend_Tree_Length = QtGui.QAction(parent=MainWindow)
        self.actionExtend_Tree_Length.setEnabled(False)
        self.actionExtend_Tree_Length.setObjectName("actionExtend_Tree_Length")
        self.actionReduce_Tree_Length = QtGui.QAction(parent=MainWindow)
        self.actionReduce_Tree_Length.setEnabled(False)
        self.actionReduce_Tree_Length.setObjectName("actionReduce_Tree_Length")
        self.actionExport_Current_Color_Map_as_csv = QtGui.QAction(parent=MainWindow)
        self.actionExport_Current_Color_Map_as_csv.setObjectName("actionExport_Current_Color_Map_as_csv")
        self.actionSave_Color_Map_Template_as_csv = QtGui.QAction(parent=MainWindow)
        self.actionSave_Color_Map_Template_as_csv.setObjectName("actionSave_Color_Map_Template_as_csv")
        self.actionImport_Color_Map = QtGui.QAction(parent=MainWindow)
        self.actionImport_Color_Map.setObjectName("actionImport_Color_Map")
        self.actionOpen_SpacerPlacer_Experiment = QtGui.QAction(parent=MainWindow)
        self.actionOpen_SpacerPlacer_Experiment.setObjectName("actionOpen_SpacerPlacer_Experiment")
        self.actionNone = QtGui.QAction(parent=MainWindow)
        self.actionNone.setObjectName("actionNone")
        self.actionCollapse_Singular_Leaf_Acquisitions = QtGui.QAction(parent=MainWindow)
        self.actionCollapse_Singular_Leaf_Acquisitions.setCheckable(True)
        self.actionCollapse_Singular_Leaf_Acquisitions.setEnabled(False)
        self.actionCollapse_Singular_Leaf_Acquisitions.setObjectName("actionCollapse_Singular_Leaf_Acquisitions")
        self.actionShow_Tags_for_Template_and_Org_Names = QtGui.QAction(parent=MainWindow)
        self.actionShow_Tags_for_Template_and_Org_Names.setCheckable(True)
        self.actionShow_Tags_for_Template_and_Org_Names.setChecked(True)
        self.actionShow_Tags_for_Template_and_Org_Names.setEnabled(False)
        self.actionShow_Tags_for_Template_and_Org_Names.setObjectName("actionShow_Tags_for_Template_and_Org_Names")
        self.actionHighlight_Singular_Leaf_Acquisions = QtGui.QAction(parent=MainWindow)
        self.actionHighlight_Singular_Leaf_Acquisions.setCheckable(True)
        self.actionHighlight_Singular_Leaf_Acquisions.setObjectName("actionHighlight_Singular_Leaf_Acquisions")
        self.actionBlinking_Highlights = QtGui.QAction(parent=MainWindow)
        self.actionBlinking_Highlights.setCheckable(True)
        self.actionBlinking_Highlights.setChecked(True)
        self.actionBlinking_Highlights.setObjectName("actionBlinking_Highlights")
        self.actionStatic_Highlights = QtGui.QAction(parent=MainWindow)
        self.actionStatic_Highlights.setCheckable(True)
        self.actionStatic_Highlights.setObjectName("actionStatic_Highlights")
        self.actionHighlight_Spacers_with_Duplicates = QtGui.QAction(parent=MainWindow)
        self.actionHighlight_Spacers_with_Duplicates.setCheckable(True)
        self.actionHighlight_Spacers_with_Duplicates.setObjectName("actionHighlight_Spacers_with_Duplicates")
        self.actionSet_Tiny_Tree_Scale = QtGui.QAction(parent=MainWindow)
        self.actionSet_Tiny_Tree_Scale.setObjectName("actionSet_Tiny_Tree_Scale")
        self.actionReset_Tree_Scale = QtGui.QAction(parent=MainWindow)
        self.actionReset_Tree_Scale.setObjectName("actionReset_Tree_Scale")
        self.menuOpen_Recent.addAction(self.actiontest)
        self.menuFile.addAction(self.actionOpen_SpacerPlacer_Experiment)
        self.menuFile.addAction(self.menuOpen_Recent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExport_as_Pdf)
        self.menuFile.addAction(self.actionExport_as_Png)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClear)
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionCopy_Image)
        self.menuEdit.addSeparator()
        self.menuView.addAction(self.actionZoom_In)
        self.menuView.addAction(self.actionZoom_Out)
        self.menuView.addSeparator()
        self.menuWindow.addAction(self.actionMinimize)
        self.menuWindow.addAction(self.actionZoom)
        self.menuHelp.addAction(self.actionAbout)
        self.menuTree.addAction(self.actionPool_Evolutionary_Events)
        self.menuTree.addSeparator()
        self.menuTree.addAction(self.actionExtend_Tree_Length)
        self.menuTree.addAction(self.actionReduce_Tree_Length)
        self.menuTree.addSeparator()
        self.menuTree.addAction(self.actionSet_Tiny_Tree_Scale)
        self.menuTree.addAction(self.actionReset_Tree_Scale)
        self.menuArrays.addAction(self.actionShow_Template)
        self.menuArrays.addAction(self.actionShow_Original_Names)
        self.menuArrays.addAction(self.actionShow_Tags_for_Template_and_Org_Names)
        self.menuArrays.addSeparator()
        self.menuArrays.addAction(self.actionCollapse_Singular_Leaf_Acquisitions)
        self.menuArrays.addAction(self.actionHighlight_Singular_Leaf_Acquisions)
        self.menuArrays.addSeparator()
        self.menuArrays.addAction(self.actionHighlight_Spacers_with_Duplicates)
        self.menuColor_By_Metadata.addAction(self.actiontest_4)
        self.menuColor_By_Imported_Color_Map.addAction(self.actionNone)
        self.menuColors.addAction(self.menuColor_By_Metadata.menuAction())
        self.menuColors.addAction(self.menuColor_By_Imported_Color_Map.menuAction())
        self.menuColors.addAction(self.actionSingle_Color_Mode)
        self.menuColors.addAction(self.actionTwo_Color_Mode)
        self.menuColors.addSeparator()
        self.menuColors.addAction(self.actionSplit_Event_Colors_Horizontal)
        self.menuColors.addAction(self.actionSplit_Event_Colors_InnerOuter)
        self.menuColors.addSeparator()
        self.menuColors.addAction(self.actionExport_Current_Color_Map_as_csv)
        self.menuColors.addAction(self.actionSave_Color_Map_Template_as_csv)
        self.menuColors.addAction(self.actionImport_Color_Map)
        self.menuColors.addSeparator()
        self.menuColors.addAction(self.actionBlinking_Highlights)
        self.menuColors.addAction(self.actionStatic_Highlights)
        self.menuColors.addSeparator()
        self.menuColors.addAction(self.actionShow_Spacerfrequency_at_Distance)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuTree.menuAction())
        self.menubar.addAction(self.menuArrays.menuAction())
        self.menubar.addAction(self.menuColors.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOpen_Recent.setTitle(_translate("MainWindow", "Open Recent"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuWindow.setTitle(_translate("MainWindow", "Window"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuTree.setTitle(_translate("MainWindow", "Tree"))
        self.menuArrays.setTitle(_translate("MainWindow", "Arrays"))
        self.menuColors.setTitle(_translate("MainWindow", "Colors"))
        self.menuColor_By_Metadata.setTitle(_translate("MainWindow", "Color By Metadata..."))
        self.menuColor_By_Imported_Color_Map.setTitle(_translate("MainWindow", "Color By Imported Color Map"))
        self.actionExport_as_Pdf.setText(_translate("MainWindow", "Export as Pdf"))
        self.actionExport_as_Png.setText(_translate("MainWindow", "Export as Png"))
        self.actionExit.setText(_translate("MainWindow", "Quit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionRedo.setText(_translate("MainWindow", "Redo"))
        self.actionCopy_Image.setText(_translate("MainWindow", "Copy Image"))
        self.actionClear.setText(_translate("MainWindow", "Clear"))
        self.actionZoom_In.setText(_translate("MainWindow", "Zoom In"))
        self.actionZoom_Out.setText(_translate("MainWindow", "Zoom Out"))
        self.actionShow_Array.setText(_translate("MainWindow", "Show Array"))
        self.actionShow_Tree.setText(_translate("MainWindow", "Show Tree"))
        self.actionsmyck.setText(_translate("MainWindow", "smyck"))
        self.action246.setText(_translate("MainWindow", "246"))
        self.actionSingle_Color_Mode.setText(_translate("MainWindow", "Single Color Mode"))
        self.actionTwo_Color_Mode.setText(_translate("MainWindow", "Two Color Mode"))
        self.actionMinimize.setText(_translate("MainWindow", "Minimize"))
        self.actionZoom.setText(_translate("MainWindow", "Zoom"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actiontest.setText(_translate("MainWindow", "test"))
        self.actiontest_2.setText(_translate("MainWindow", "test"))
        self.actionshow_tree.setText(_translate("MainWindow", "Show Tree"))
        self.actionShow_Spacers.setText(_translate("MainWindow", "Show Spacers"))
        self.actionShow_Template.setText(_translate("MainWindow", "Show Template"))
        self.actionShow_Original_Names.setText(_translate("MainWindow", "Show Original Names"))
        self.actionShow_Edge_Length.setText(_translate("MainWindow", "Show Edge Length"))
        self.actionShow_Evolutionary_Events.setText(_translate("MainWindow", "Show Evolutionary Events"))
        self.actionPool_Evolutionary_Events.setText(_translate("MainWindow", "Pool Evolutionary Events"))
        self.actionShow_Short_Tree.setText(_translate("MainWindow", "Show Short Tree"))
        self.actiontest_3.setText(_translate("MainWindow", "test"))
        self.actionHorizontal_Color_Split.setText(_translate("MainWindow", "Horizontal Color Split"))
        self.actionInner_Outer_Color_Split.setText(_translate("MainWindow", "Inner-Outer Color Split"))
        self.actionSplit_Event_Colors_Horizontal.setText(_translate("MainWindow", "Horizontal Two Color Event Split"))
        self.actionSplit_Event_Colors_InnerOuter.setText(_translate("MainWindow", "InnerOuter Two Color Event Split"))
        self.actiontest_4.setText(_translate("MainWindow", "test"))
        self.actionShow_Spacerfrequency_at_Distance.setText(_translate("MainWindow", "Show Spacerfrequency at Distance"))
        self.actionShow_Original_Tree.setText(_translate("MainWindow", "Show Original Tree"))
        self.actionShow_Root_Events_as_Array.setText(_translate("MainWindow", "Show Root Events as Array"))
        self.actionCollapse_Leaf_Acquisitions_in_Array.setText(_translate("MainWindow", "Collapse Leaf Acquisitions in Array"))
        self.actionExtend_Tree_Length.setText(_translate("MainWindow", "&Extend Tree Length"))
        self.actionReduce_Tree_Length.setText(_translate("MainWindow", "&Reduce Tree Length"))
        self.actionExport_Current_Color_Map_as_csv.setText(_translate("MainWindow", "Save Current Color Map to .csv"))
        self.actionSave_Color_Map_Template_as_csv.setText(_translate("MainWindow", "Save Color Map Template to .csv"))
        self.actionImport_Color_Map.setText(_translate("MainWindow", "Import Color Map"))
        self.actionOpen_SpacerPlacer_Experiment.setText(_translate("MainWindow", "Open SpacerPlacer Experiment..."))
        self.actionNone.setText(_translate("MainWindow", "None"))
        self.actionCollapse_Singular_Leaf_Acquisitions.setText(_translate("MainWindow", "Collapse Singular Leaf Acquisitions"))
        self.actionShow_Tags_for_Template_and_Org_Names.setText(_translate("MainWindow", "Show Tags for Template and Org Names"))
        self.actionHighlight_Singular_Leaf_Acquisions.setText(_translate("MainWindow", "Highlight Singular Leaf Acquisions"))
        self.actionBlinking_Highlights.setText(_translate("MainWindow", "Blinking Highlights"))
        self.actionStatic_Highlights.setText(_translate("MainWindow", "Static Black and White Highlights"))
        self.actionHighlight_Spacers_with_Duplicates.setText(_translate("MainWindow", "Highlight Spacers with Duplicates"))
        self.actionSet_Tiny_Tree_Scale.setText(_translate("MainWindow", "Set Tiny Tree Scale"))
        self.actionReset_Tree_Scale.setText(_translate("MainWindow", "Reset Tree Scale"))