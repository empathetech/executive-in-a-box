# Tailscale Guide

This guide explains how to make Executive in a Box accessible to your whole team
using Tailscale — so anyone on your team can use the same instance from their own
device, without hosting anything in the cloud.

---

## What is Tailscale?

Tailscale creates a private, encrypted network between your devices and your
teammates' devices. Think of it as a secure tunnel — your teammate's laptop
and your server act like they're on the same local network, even if they're
in different locations.

Tailscale is free for small teams (up to 3 users on the free plan).
Download it at https://tailscale.com.

---

## What this enables

Without Tailscale: only you can access Executive in a Box, on the same machine
where it's running.

With Tailscale: anyone on your Tailscale network can access your Executive in a
Box instance from their browser, on any device, from anywhere.

**Important:** Tailscale is the access control. Anyone who can join your Tailscale
network can access the app — there is no separate login or password on the app
itself in this version. Only invite people to your Tailscale network that you
trust with full access to your org's strategic context.

---

## Setup

### Step 1: Install Tailscale on the machine running Executive in a Box

Go to https://tailscale.com/download and install Tailscale for your operating system.
Follow the on-screen instructions. You'll need to create a free Tailscale account.

When Tailscale is installed and running, your machine gets a Tailscale IP address.
Find it by running:

```
tailscale ip -4
```

You'll see something like: `100.64.x.x` — this is your Tailscale IP.

### Step 2: Start Executive in a Box on your Tailscale IP

```
exec-in-a-box web --host 0.0.0.0
```

The `--host 0.0.0.0` flag makes the web app accessible on all network interfaces,
including your Tailscale IP. (By default it only accepts connections from your
own machine.)

You should see:

```
Executive in a Box — web app running at http://0.0.0.0:8080
Press Ctrl+C to stop.
```

### Step 3: Install Tailscale on each teammate's device

Each teammate needs to install Tailscale and join your network:
1. Go to https://tailscale.com/download and install
2. Log into the same Tailscale account (or accept an invite to your network)

### Step 4: Share your Tailscale IP with your team

Tell your teammates to open their browser and go to:

```
http://100.64.x.x:8080
```

(Replace `100.64.x.x` with the Tailscale IP you found in Step 1.)

---

## Keeping it running

The web app only runs while you have `exec-in-a-box web` running in your terminal.
If you want it to stay running after you close your terminal, you can run it in
the background:

**macOS / Linux:**
```
nohup exec-in-a-box web --host 0.0.0.0 &
```

To stop it later:
```
pkill -f "exec-in-a-box web"
```

**Windows:** Use Task Scheduler or run it in a separate terminal window you leave open.

---

## Troubleshooting

**"I can't reach it from my teammate's device"**
- Make sure Tailscale is running on both devices (look for the Tailscale icon in your
  taskbar/menu bar)
- Make sure you used `--host 0.0.0.0` when starting the web app
- Check that both devices are on the same Tailscale network (same account)

**"The port is already in use"**
Use a different port: `exec-in-a-box web --host 0.0.0.0 --port 9000`

---

## A note on security

Tailscale encrypts all traffic between devices. Your org's strategic data does not
travel over the public internet — it stays within your Tailscale network.

That said, anyone on your Tailscale network has full access to the app. Keep your
Tailscale network limited to people you trust. See [SECURITY_PRIVACY.md](../hacky-hours/02-design/SECURITY_PRIVACY.md)
for the full trust boundary analysis.
