namespace SKClean
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
            this.buttonClean = new System.Windows.Forms.Button();
            this.optionLeave = new System.Windows.Forms.CheckBox();
            this.SuspendLayout();
            // 
            // buttonClean
            // 
            this.buttonClean.Location = new System.Drawing.Point(12, 12);
            this.buttonClean.Name = "buttonClean";
            this.buttonClean.Size = new System.Drawing.Size(81, 38);
            this.buttonClean.TabIndex = 0;
            this.buttonClean.Text = "C L E A N";
            this.buttonClean.UseVisualStyleBackColor = true;
            this.buttonClean.Click += new System.EventHandler(this.buttonClean_Click);
            // 
            // optionLeave
            // 
            this.optionLeave.AutoSize = true;
            this.optionLeave.Location = new System.Drawing.Point(12, 56);
            this.optionLeave.Name = "optionLeave";
            this.optionLeave.Size = new System.Drawing.Size(81, 17);
            this.optionLeave.TabIndex = 1;
            this.optionLeave.Text = "Leave Chat";
            this.optionLeave.UseVisualStyleBackColor = true;
            // 
            // Main
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(105, 85);
            this.Controls.Add(this.optionLeave);
            this.Controls.Add(this.buttonClean);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.MaximumSize = new System.Drawing.Size(115, 118);
            this.MinimizeBox = false;
            this.MinimumSize = new System.Drawing.Size(115, 118);
            this.Name = "Main";
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "SKClean";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button buttonClean;
        private System.Windows.Forms.CheckBox optionLeave;

    }
}

