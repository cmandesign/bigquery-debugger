import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import java.awt.FileDialog
import java.awt.Frame
import java.io.BufferedReader
import java.io.FileReader

@Composable
fun BigDebugApp() {
    var textValue by remember { mutableStateOf("") }
    var button2Clicked by remember { mutableStateOf(false) }

    var selectedFileContent by remember { mutableStateOf<String?>(null) }

    MaterialTheme {
        Box(modifier = Modifier.fillMaxSize()) {
            Row(modifier = Modifier.fillMaxSize()) {
                // Left column in blue
                Column(
                    modifier = Modifier.width(150.dp).fillMaxHeight().background(Color.Blue)
                ) {
                    Button(
                        onClick = {
                            val fileDialog = FileDialog(Frame(), "Select a file", FileDialog.LOAD)
                            fileDialog.isVisible = true
                            val selectedFile = fileDialog.file
                            val selectedFilePath = fileDialog.directory + selectedFile
                            if (selectedFile != null) {
                                loadFileContent(selectedFilePath) { content ->
                                    selectedFileContent = content
                                    textValue = content
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth().padding(16.dp)
                    ) {
                        Text("Open file")
                    }

                    Button(
                        onClick = {
                            button2Clicked = true
                        },
                        modifier = Modifier.fillMaxWidth().padding(16.dp)
                    ) {
                        Text("Button 2")
                    }
                }

                // Right column with a text box
                Column(
                    modifier = Modifier.fillMaxSize().background(Color.Black)
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize()
                    ) {
                        BasicTextField(
                            value = selectedFileContent ?: textValue,
                            onValueChange = {
                                selectedFileContent = it
                                textValue = it
                            },
                            textStyle = TextStyle(color = Color.White)
                        )
                    }
                }
            }
        }
    }
}

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "Kotlin Compose Debug App"
    ) {
        BigDebugApp()
    }
}

fun loadFileContent(filePath: String, callback: (String) -> Unit) {
    runBlocking {
        launch(Dispatchers.IO) {
            val file = FileReader(filePath)
            val reader = BufferedReader(file)
            val content = reader.readText()
            reader.close()
            callback(content)
        }
    }
}
