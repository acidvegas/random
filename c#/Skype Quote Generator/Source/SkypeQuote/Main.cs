using System;
using System.Globalization;
using System.IO;
using System.Text;
using System.Windows.Forms;


namespace SkypeQuote {
    public partial class Main : Form {
        private static readonly DateTime LinuxTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);

        public Main() {
            InitializeComponent();
        }

        private void Main_Load(object sender, EventArgs e) {
            this.TimeBox.Text = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        }

        private void NowButton_Click(object sender, EventArgs e) {
            this.TimeBox.Text = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        }

        private void CopyButton_Click(object sender, EventArgs e) {
            Clipboard.SetText(" ");
            DateTime dateTime;
            if (!DateTime.TryParse(this.TimeBox.Text, out dateTime)) {
                System.Windows.Forms.MessageBox.Show("Invalid timestamp format!");
                return;
            }
            string user = this.NameBox.Text;
            string message = this.MessageBox.Text;
            string skypeMessageFragment = String.Format("<quote author=\"{0}\" timestamp=\"{1}\">{2}</quote>", user, (dateTime.ToUniversalTime() - LinuxTime).TotalSeconds, message);
            IDataObject dataObject = new DataObject();
            dataObject.SetData("System.String", message);
            dataObject.SetData("Text", message);
            dataObject.SetData("UnicodeText", message);
            dataObject.SetData("OEMText", message);
            dataObject.SetData("SkypeMessageFragment", new MemoryStream(Encoding.UTF8.GetBytes(skypeMessageFragment)));
            dataObject.SetData("Locale", new MemoryStream(BitConverter.GetBytes(CultureInfo.CurrentCulture.LCID)));
            Clipboard.SetDataObject(dataObject);
        }
    }
}
