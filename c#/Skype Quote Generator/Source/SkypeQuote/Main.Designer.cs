namespace SkypeQuote
{
    partial class Main
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Main));
            this.NameBox = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.TimeBox = new System.Windows.Forms.TextBox();
            this.MessageBox = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.CopyButton = new System.Windows.Forms.Button();
            this.NowButton = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // NameBox
            // 
            this.NameBox.Location = new System.Drawing.Point(79, 10);
            this.NameBox.Name = "NameBox";
            this.NameBox.Size = new System.Drawing.Size(158, 20);
            this.NameBox.TabIndex = 0;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(13, 13);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(38, 13);
            this.label1.TabIndex = 1;
            this.label1.Text = "Name:";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 39);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(61, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "Timestamp:";
            // 
            // TimeBox
            // 
            this.TimeBox.Location = new System.Drawing.Point(79, 38);
            this.TimeBox.Name = "TimeBox";
            this.TimeBox.Size = new System.Drawing.Size(114, 20);
            this.TimeBox.TabIndex = 3;
            // 
            // MessageBox
            // 
            this.MessageBox.Location = new System.Drawing.Point(79, 65);
            this.MessageBox.Multiline = true;
            this.MessageBox.Name = "MessageBox";
            this.MessageBox.Size = new System.Drawing.Size(158, 69);
            this.MessageBox.TabIndex = 4;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(12, 68);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(53, 13);
            this.label3.TabIndex = 5;
            this.label3.Text = "Message:";
            // 
            // CopyButton
            // 
            this.CopyButton.Location = new System.Drawing.Point(12, 140);
            this.CopyButton.Name = "CopyButton";
            this.CopyButton.Size = new System.Drawing.Size(225, 23);
            this.CopyButton.TabIndex = 6;
            this.CopyButton.Text = "Copy To Clipboard";
            this.CopyButton.UseVisualStyleBackColor = true;
            this.CopyButton.Click += new System.EventHandler(this.CopyButton_Click);
            // 
            // NowButton
            // 
            this.NowButton.Location = new System.Drawing.Point(199, 36);
            this.NowButton.Name = "NowButton";
            this.NowButton.Size = new System.Drawing.Size(38, 23);
            this.NowButton.TabIndex = 7;
            this.NowButton.Text = "Now";
            this.NowButton.UseVisualStyleBackColor = true;
            this.NowButton.Click += new System.EventHandler(this.NowButton_Click);
            // 
            // Main
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(249, 170);
            this.Controls.Add(this.NowButton);
            this.Controls.Add(this.CopyButton);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.MessageBox);
            this.Controls.Add(this.TimeBox);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.NameBox);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MaximumSize = new System.Drawing.Size(265, 209);
            this.MinimizeBox = false;
            this.MinimumSize = new System.Drawing.Size(265, 209);
            this.Name = "Main";
            this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Skype Quote Generator";
            this.Load += new System.EventHandler(this.Main_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox NameBox;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox TimeBox;
        private System.Windows.Forms.TextBox MessageBox;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Button CopyButton;
        private System.Windows.Forms.Button NowButton;
    }
}

