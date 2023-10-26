import androidx.compose.desktop.ui.tooling.preview.Preview
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle

@Composable
fun BigDebugApp() {
    var textValue by remember { mutableStateOf("") }
    var button1Clicked by remember { mutableStateOf(false) }
    var button2Clicked by remember { mutableStateOf(false) }

    MaterialTheme {
        Box(modifier = Modifier.fillMaxSize()) {
            Row(modifier = Modifier.fillMaxSize()) {
                // Left column in blue
                Column(
                    modifier = Modifier.width(150.dp).fillMaxHeight().background(Color.Blue)
                ) {
                    Button(
                        onClick = {
                            button1Clicked = true
                            button2Clicked = false
                        },
                        modifier = Modifier.fillMaxWidth().padding(16.dp)
                    ) {
                        Text("Button 1")
                    }

                    Button(
                        onClick = {
                            button1Clicked = false
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
                    BasicTextField(
                        value = textValue,
                        onValueChange = { textValue = it },
                        modifier = Modifier.fillMaxSize(),
                        textStyle = TextStyle(color = Color.White)
                    )
                }
            }
        }
    }
}

fun main() = application {
    Window(onCloseRequest = ::exitApplication) {
        BigDebugApp()
    }
}
