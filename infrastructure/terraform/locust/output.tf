output "locust_master_public_ip" {
  value = aws_instance.locust_master.public_ip
}
