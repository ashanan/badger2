Vagrant::Config.run do |config|

    config.vm.box = "centos-56-32"
    config.vm.box_url = "http://people.mozilla.com/~lorchard/vm/centos-56-32.box"

    # Increase vagrant's patience during hang-y CentOS bootup
    # see: https://github.com/jedi4ever/veewee/issues/14
    config.ssh.max_tries = 50
    config.ssh.timeout   = 300

    config.vm.share_folder("v-root", "/vagrant", ".", :nfs => true)

    # Add to /etc/hosts: 33.33.33.24 dev.badger.mozilla.org
    config.vm.network "33.33.33.24"

    config.vm.provision :puppet do |puppet|
        puppet.manifests_path = "puppet/manifests"
        puppet.manifest_file  = "dev-vagrant.pp"
    end

end
