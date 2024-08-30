import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QFileDialog, QSlider, QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import csvProcessor 

class plotCsv(QMainWindow):
    def __init__(self, directory):
        super().__init__()

        self.ultimate_data = {}
        self.typeParameters = []
        self.keysSelected = []

        self.setWindowTitle("Plotter")
        self.setGeometry(300, 100, 800, 600)
        
        self.directory_button = QPushButton("Select Directory")
        self.directory_button.clicked.connect(self.open_directory_dialog)

        self.model = QFileSystemModel()
        self.model.setRootPath(directory)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(directory))
        self.tree.setColumnWidth(0, 250)
        self.tree.setSelectionMode(QTreeView.MultiSelection)
        self.tree.clicked.connect(self.on_tree_view_clicked)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.list_widget.setEnabled(False)
        self.list_widget.itemSelectionChanged.connect(self.on_item_selection_changed)

        self.plot_button = QPushButton("PLOT")
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.plot_selected_keys)

        self.export_button = QPushButton("EXPORT")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_graph)

        self.refresh_button = QPushButton("REFRESH")
        self.refresh_button.setEnabled(False)
        self.refresh_button.clicked.connect(self.refresh_keys)

        self.x_slider_start = QSlider(Qt.Horizontal)
        self.x_slider_start.setRange(0, 100)
        self.x_slider_start.setValue(0)
        self.x_slider_start.valueChanged.connect(self.update_plot_range)

        self.x_slider_end = QSlider(Qt.Horizontal)
        self.x_slider_end.setRange(0, 100)
        self.x_slider_end.setValue(100)
        self.x_slider_end.valueChanged.connect(self.update_plot_range)

        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(100, 2000) 
        self.width_slider.setValue(800)  

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(100, 2000)  
        self.height_slider.setValue(600) 

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter graph title")
        self.title_input.textChanged.connect(self.update_plot_title)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Set up the layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.plot_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.refresh_button)

        x_slider_layout = QHBoxLayout()
        x_slider_layout.addWidget(QLabel("Start Time"))
        x_slider_layout.addWidget(self.x_slider_start)
        x_slider_layout.addWidget(QLabel("End Time"))
        x_slider_layout.addWidget(self.x_slider_end)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Graph Title"))
        layout.addWidget(self.title_input)
        layout.addLayout(button_layout)
        layout.addLayout(x_slider_layout)

        image_dimension_layout = QHBoxLayout()
        image_dimension_layout.addWidget(QLabel("Width"))
        image_dimension_layout.addWidget(self.width_slider)
        image_dimension_layout.addWidget(QLabel("Height"))
        image_dimension_layout.addWidget(self.height_slider)

        
        layout.addLayout(image_dimension_layout)
        layout.addWidget(self.directory_button)
        fileAndListLayout = QHBoxLayout()
        fileAndListLayout.addWidget(self.tree)
        fileAndListLayout.addWidget(self.list_widget)
        layout.addLayout(fileAndListLayout)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.first_selected_index = None
        self.last_selected_index = None

        self.time = None  

    def open_directory_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.model.setRootPath(directory)
            self.tree.setRootIndex(self.model.index(directory))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.tree.clearSelection()
            self.list_widget.clear()

    def on_tree_view_clicked(self, index):
        selected_files = [self.model.filePath(i) for i in self.tree.selectedIndexes() if self.model.filePath(i).endswith('.csv')]
        if selected_files:
            self.selected_csv_files = selected_files
            self.refresh_button.setEnabled(True)
            self.load_keys(selected_files[0])  
        else:
            self.selected_csv_files = []
            self.plot_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.list_widget.setEnabled(False)

    def load_keys(self, file_path):
    
        keys = csvProcessor.getKeys(file_path)
        self.keys = keys
        self.list_widget.clear()
        for key in keys:
            item = QListWidgetItem(self.list_widget)
            self.list_widget.addItem(item)
            
           
            key_item_widget = KeyItemWidget(key)
            item.setSizeHint(key_item_widget.sizeHint())
            self.list_widget.setItemWidget(item, key_item_widget)
        self.list_widget.setEnabled(True)
        

    def on_item_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.plot_button.setEnabled(True)
        else:
            self.plot_button.setEnabled(False)
        if len(selected_items) > 1 and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            current_selected_index = self.list_widget.row(selected_items[-1])
            if self.first_selected_index is None:
                self.first_selected_index = self.list_widget.row(selected_items[0])
            self.last_selected_index = current_selected_index
            self.select_range(self.first_selected_index, self.last_selected_index)
            
           
            if selected_items:
                first_selected_item = selected_items[0]
                first_selected_widget = self.list_widget.itemWidget(first_selected_item)
                selected_parameter = first_selected_widget.combo_box.currentText()
                for item in selected_items:
                    key_item_widget = self.list_widget.itemWidget(item)
                    key_item_widget.combo_box.setCurrentText(selected_parameter)

    def select_range(self, start, end):
        for i in range(min(start, end), max(start, end) + 1):
            self.list_widget.item(i).setSelected(True)



    def plot_selected_keys(self):
        self.ultimate_data = {}
        self.time = None
        if self.selected_csv_files:
            selected_keys = []
            parameter_types = []
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                if item.isSelected():
                    key_item_widget = self.list_widget.itemWidget(item)
                    selected_keys.append(key_item_widget.label.text())
                    parameter_types.append(key_item_widget.combo_box.currentText())
            self.typeParameters = parameter_types
            self.keysSelected = selected_keys
            self.process_csv_files(self.selected_csv_files, selected_keys, parameter_types)
            self.plot_button.setEnabled(False)
            self.export_button.setEnabled(True)


    def process_csv_files(self, file_paths, selected_keys, parameter_types):
        for file_path in sorted(list(set(file_paths))):
            
            _, data, _ = csvProcessor.processData(file_path)
            
            if self.ultimate_data == {}:
                self.ultimate_data = data
            else:
                self.ultimate_data = csvProcessor.mergeDict(self.ultimate_data, data)

        time = self.ultimate_data["TimeStep"]
        self.time = time  
        
        try:
            self.plot_data(time, self.ultimate_data, selected_keys, parameter_types)
        except:
            pass
    

    def plot_data(self, time, data, selected_keys, parameter_types):
        x_start_value = min(time) + (max(time) - min(time)) * (self.x_slider_start.value() / 100.0)
        x_end_value = min(time) + (max(time) - min(time)) * (self.x_slider_end.value() / 100.0)

        # Clear all existing axes
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        axes = {parameter_types[0]: self.ax}
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_index = 0

        for key, param_type in zip(selected_keys, parameter_types):
            if param_type not in axes:
                axes[param_type] = self.ax.twinx()
                axes[param_type].spines['right'].set_position(('outward', 0))
                
            axes[param_type].set_ylabel(param_type)
            axes[param_type].tick_params(axis='y', colors= 'black')

            if len(time) == len(data[key]):
                axes[param_type].plot(time, data[key], label=key, color=colors[color_index % len(colors)])
            else:
                min_length = min(len(time), len(data[key]))
                axes[param_type].plot(time[:min_length], data[key][:min_length], label=key, color=colors[color_index % len(colors)])
            color_index += 1

        self.ax.set_xlim([x_start_value, x_end_value])
        self.ax.set_xlabel('Time')
        self.ax.set_title(self.title_input.text() if self.title_input.text() else '')

        handles, labels = [], []
        for ax in axes.values():
            for handle, label in zip(*ax.get_legend_handles_labels()):
                handles.append(handle)
                labels.append(label)
        self.ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.02, 1))
        self.canvas.draw()
        
    def update_plot_range(self):
        if self.time is not None:
            self.plot_data(self.time, self.ultimate_data, self.keysSelected,self.typeParameters)

        if self.x_slider_start.value() > self.x_slider_end.value():
            self.x_slider_start.setValue(self.x_slider_end.value())


    def update_plot_title(self):
        if self.time is not None:
            self.plot_data(self.time, self.ultimate_data, self.keysSelected,self.typeParameters)

    def export_graph(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph As", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)
        if file_path:

            export_figure, export_ax = plt.subplots()
            

            export_axes = {}
            colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
            color_index = 0

            for key, param_type in zip(self.keysSelected, self.typeParameters):
                if param_type not in export_axes:
                    if len(export_axes) == 0:
                        export_axes[param_type] = export_ax
                    else:
                        export_axes[param_type] = export_ax.twinx()
                        export_axes[param_type].spines['right'].set_position(('outward', 0))  
                    export_axes[param_type].set_ylabel(param_type)
                    export_axes[param_type].tick_params(axis='y', colors=colors[color_index])
                    

                if len(self.time) == len(self.ultimate_data[key]):
                    export_axes[param_type].plot(self.time, self.ultimate_data[key], label=key, color=colors[color_index % len(colors)])
                else:
                    min_length = min(len(self.time), len(self.ultimate_data[key]))
                    export_axes[param_type].plot(self.time[:min_length], self.ultimate_data[key][:min_length], label=key, color=colors[color_index % len(colors)])
                color_index += 1

            x_start_value = min(self.time) + (max(self.time) - min(self.time)) * (self.x_slider_start.value() / 100.0)
            x_end_value = min(self.time) + (max(self.time) - min(self.time)) * (self.x_slider_end.value() / 100.0)
            

            export_ax.set_xlim([x_start_value, x_end_value])
            
            width = self.width_slider.value() / 100  
            height = self.height_slider.value() / 100  
            export_figure.set_size_inches(width, height)
            

            handles, labels = [], []
            for ax in export_axes.values():
                for handle, label in zip(*ax.get_legend_handles_labels()):
                    handles.append(handle)
                    labels.append(label)
            export_ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)  
            export_ax.set_title(self.title_input.text() if self.title_input.text() else '')

            export_figure.savefig(file_path, bbox_inches='tight')
            
            plt.close(export_figure) 
            
            self.export_button.setEnabled(False)
    def refresh_keys(self):
        self.figure.clear()
        self.canvas.draw()
        self.list_widget.clearSelection()
        self.first_selected_index = None
        self.last_selected_index = None
        self.export_button.setEnabled(False)
        self.ultimate_data = {}
        self.time = None
        self.typeParameters = []
        self.keysSelected = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            key_item_widget = self.list_widget.itemWidget(item)
            key_item_widget.combo_box.setCurrentText("")

class KeyItemWidget(QWidget):
    def __init__(self, key):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.label = QLabel(key)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["","Voltage (V)", "Current (A)", "Temperature (°C)", "Power (W)"])
        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)
        self.setLayout(layout)

if __name__ == "__main__":
    directory = r'' 
    app = QApplication(sys.argv)
    window = plotCsv(directory)
    window.show()
    sys.exit(app.exec_())
