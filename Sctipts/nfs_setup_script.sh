#!/bin/bash

# Stop the script on any error
set -e

# Get the volume name and configuration type as parameters
VOLUME_NAME=$1
CONFIG_TYPE=$2
MOUNT_POINT="/mnt/jenkins"

if [[ -z "$VOLUME_NAME" ]] || [[ -z "$CONFIG_TYPE" ]]; then
  echo "Usage: $0 <volume-device-name> <config-type>"
  echo "Example: $0 /dev/xvdbi swarm"
  echo "Example: $0 /dev/xvdbi single"
  exit 1
fi

# Check if the disk exists
if ! lsblk | grep -q "$(basename "$VOLUME_NAME")"; then
  echo "Error: Disk $VOLUME_NAME does not exist. Please provide a valid disk."
  exit 1
fi

# Install required packages for NFS
echo "### Installing required packages for NFS"
apt update
apt install -y nfs-server

# Mode-specific setup
if [[ "$CONFIG_TYPE" == "single" ]]; then
  echo "### Configuring for single instance"

  # Prompt for IPs
  read -p "Enter the IP address of the single node to export to: " NODE_IP
  read -p "Is there an agent configured? (yes/no): " AGENT_CONFIGURED

  # Update /etc/hosts with the provided IPs
  echo "### Adding single node IP to /etc/hosts"
  echo "$NODE_IP single-node" >> /etc/hosts

  if [[ "$AGENT_CONFIGURED" == "yes" ]]; then
    read -p "Enter the IP address of the agent: " AGENT_IP
    echo "### Adding agent IP to /etc/hosts"
    echo "$AGENT_IP agent" >> /etc/hosts
  fi

  # Create NFS export entry for the single node
  NODE_ENTRIES="$MOUNT_POINT single-node(rw,sync,no_root_squash,no_subtree_check)"

elif [[ "$CONFIG_TYPE" == "swarm" ]]; then
  echo "### Configuring for swarm cluster"

  # Prompt for swarm node IPs
  read -p "Enter swarm node names separated by space (e.g., swarm1 swarm2 swarm3): " SWARM_NODES
  NODE_ENTRIES=""
  for NODE in $SWARM_NODES; do
    read -p "Enter IP for $NODE: " NODE_IP
    echo "$NODE_IP $NODE" >> /etc/hosts
    NODE_ENTRIES+="$MOUNT_POINT $NODE(rw,sync,no_root_squash,no_subtree_check)
"
  done
else
  echo "Invalid config type. Use 'swarm' or 'single'."
  exit 1
fi

# Check if the partition is already mounted
if mount | grep -q "${VOLUME_NAME}1"; then
  echo "The partition ${VOLUME_NAME}1 is already mounted. Unmounting it now..."
  umount "${VOLUME_NAME}1"
fi

echo "### Step 1: Creating partition on $VOLUME_NAME"
# Create a new partition if not already partitioned
if ! fdisk -l "$VOLUME_NAME" | grep -q "${VOLUME_NAME}1"; then
  echo -e "n
p
1


w" | fdisk "$VOLUME_NAME"
else
  echo "Partition ${VOLUME_NAME}1 already exists. Skipping partition creation."
fi

echo "### Step 2: Formatting the partition"
# Format the partition only if it’s not already formatted
if ! blkid "${VOLUME_NAME}1" | grep -q ext4; then
  mkfs.ext4 "${VOLUME_NAME}1"
else
  echo "Partition ${VOLUME_NAME}1 is already formatted. Skipping formatting."
fi

echo "### Step 3: Creating the mount directory"
# Create the mount directory
mkdir -p "$MOUNT_POINT"

echo "### Step 4: Mounting the partition to $MOUNT_POINT"
# Mount the partition
mount "${VOLUME_NAME}1" "$MOUNT_POINT"

echo "### Step 5: Adding the partition to fstab for automatic mounting"
# Update fstab
if ! grep -q "${VOLUME_NAME}1" /etc/fstab; then
  echo "${VOLUME_NAME}1 $MOUNT_POINT ext4 defaults 0 0" >> /etc/fstab
fi

echo "### Step 6: Setting permissions for the directory"
# Set ownership and permissions
chown -R 1000:1000 "$MOUNT_POINT"
chmod -R 775 "$MOUNT_POINT"

echo "### Step 7: Configuring NFS sharing"
# Add the mount point to NFS exports
if ! grep -q "$MOUNT_POINT" /etc/exports; then
  echo -e "$NODE_ENTRIES" >> /etc/exports
fi

# Restart the NFS service
echo "### Step 8: Restarting NFS service"
exportfs -a
systemctl restart nfs-server

echo "### NFS setup completed. $MOUNT_POINT is ready for use."