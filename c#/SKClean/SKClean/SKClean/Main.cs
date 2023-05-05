#region Imports
using SKYPE4COMLib;
using System;
using System.Windows.Forms;
#endregion

namespace SKClean {
    public partial class Main : Form {
        public static Skype API = new Skype();

        #region Startup
        public Main() {
            InitializeComponent();
        }
        #endregion

        #region Clean Button
        private void buttonClean_Click(object sender, EventArgs e) {
            API.Attach(5, true);
            foreach (Chat chat in API.ActiveChats) {
                foreach (ChatMessage msg in chat.Messages) {
                    if (msg.IsEditable)
                        try {
                            msg.Body = "";
                        } catch {
                            continue;
                        }
                }
                if (optionLeave.Checked) {
                    try {
                        chat.SendMessage("/topic .");
                        chat.Leave();
                    } catch {
                        continue;
                    }
                    
                }
            }
            API.ClearCallHistory();
            API.ClearChatHistory();
            API.ClearVoicemailHistory();
        }
        #endregion
    }
}
